# Yanis — le consentement expliqué ligne par ligne en français courant

Ce chapitre couvre :

- [`4e21df6 — feat(consent): add accept and withdrawal`](https://github.com/AshDv/ScribeProject/commit/4e21df68d3c0241f1ca5d9b9751e8aeaf5315daa)
- [`ecd894c — feat(consent): add public consent interface`](https://github.com/AshDv/ScribeProject/commit/ecd894ce955b396193fcc1300278517fbd4c3d35)

Le premier commit ajoute les portes backend permettant de démarrer ou arrêter une réunion, d’accepter ou retirer un consentement et de demander l’effacement. Le second ajoute la page publique utilisée par le participant.

## 1. Le parcours complet avant les détails

1. L’organisateur saisit le nom et le courriel de chaque participant.
2. Le backend crée une réunion de consentement.
3. Pour chaque participant, il fabrique un jeton aléatoire.
4. Il conserve seulement l’empreinte du jeton en base et envoie le jeton réel par courriel.
5. Le participant ouvre une adresse contenant le jeton.
6. Le backend transforme le jeton reçu en empreinte et cherche la ligne correspondante.
7. Le participant accepte ou refuse.
8. La réunion ne peut passer à l’état `RECORDING` que si tous les participants ont un consentement actif et si l’organisateur confirme l’annonce orale.
9. Un retrait place la réunion à l’état arrêté.

Un jeton est une longue valeur difficile à deviner qui donne accès à une action précise. Une empreinte est le résultat à sens unique d’une fonction de hachage : on peut recalculer l’empreinte d’un jeton reçu, mais on ne peut normalement pas retrouver le jeton original à partir de l’empreinte.

## 2. Pourquoi utiliser SHA-256 ici ne signifie pas « chiffrer »

La fonction `hashlib.sha256` calcule une empreinte de 256 bits. SHA signifie « Secure Hash Algorithm ».

Le chiffrement transforme une donnée avec une clé afin de pouvoir la récupérer en déchiffrant. Le hachage produit une empreinte non réversible utilisée pour comparer.

Ici, on ne veut pas relire le jeton original depuis la base. Lorsqu’un participant présente le jeton de son lien, le serveur recalcule son empreinte et cherche la même empreinte.

Si la base était consultée par une personne non autorisée, elle ne fournirait donc pas directement les liens encore utilisables.

## 3. Les imports de `consent_routes.py`

### `import hashlib`

Cette ligne charge le module standard qui contient SHA-256. Le nom `hashlib` devient disponible dans le fichier.

### `import secrets`

`secrets` est un module Python conçu pour fabriquer des valeurs aléatoires adaptées à la sécurité.

Il est préférable à un générateur aléatoire destiné aux simulations, car ses résultats sont beaucoup moins prévisibles.

### `from datetime import datetime`

Cette ligne importe le type représentant une date et une heure. Il sert dans le formulaire de création pour la date prévue de la réunion.

### `from pathlib import Path`

`Path` sert ici lors de l’effacement pour transformer le chemin audio enregistré en objet vérifiable.

### Imports FastAPI

`APIRouter` crée un groupe de routes. `Depends` demande à FastAPI de fournir automatiquement une dépendance comme l’utilisateur courant ou une session de base. `HTTPException` arrête une route avec un code et un message HTTP.

### Imports Pydantic

`BaseModel` sert à définir la forme d’un corps JSON valide.

`EmailStr` est un type de texte dont la forme doit ressembler à une adresse électronique. Il ne confirme pas que le destinataire existe.

`Field` ajoute des contraintes comme une longueur minimale et maximale.

### Imports SQLModel

`Session` est la conversation avec la base. `select` construit une requête de lecture.

### Imports propres à Scribe

`current_user` identifie l’utilisateur connecté à partir de son jeton.

`settings` contient la configuration.

`get_session` fournit une session de base fermée après la route.

`send_consent_email` envoie l’invitation. `EmailError` représente un échec prévu de cet envoi.

Les classes importées depuis `models` représentent les tables. Leur nom en PascalCase indique des classes :

- `ConsentSession` : une réunion préparée pour recueillir les consentements ;
- `ParticipantConsent` : un participant et l’état de son accord ;
- `Recording` : un enregistrement ;
- `SessionRecording` : le lien entre réunion et enregistrement ;
- `StructuredReport` : le compte rendu structuré ;
- `User` : un compte utilisateur.

`ConsentSessionStatus` est la liste contrôlée des états possibles. `utc_now` renvoie l’heure universelle actuelle.

## 4. `router = APIRouter(prefix="/api")`

Cette ligne crée le groupe de routes.

`prefix="/api"` ajoute automatiquement `/api` devant chaque adresse définie ensuite. La route écrite `/consent-sessions` devient donc `/api/consent-sessions`.

Le routeur doit ensuite être inclus dans l’application principale. Sans cette inclusion, les fonctions existeraient dans le fichier mais aucune URL ne les appellerait.

## 5. Les modèles d’entrée

### `class ParticipantInput(BaseModel):`

Cette classe décrit un participant reçu depuis le navigateur. Ce n’est pas encore une table de base.

```python
name: str = Field(min_length=2, max_length=100)
```

Le nom doit être du texte entre 2 et 100 caractères. La limite évite un nom vide ou un texte démesuré.

```python
email: EmailStr
```

L’adresse doit avoir une forme électronique valide. Aucune valeur par défaut n’est donnée, donc le champ est obligatoire.

### `class SessionInput(BaseModel):`

`title` doit compter entre 2 et 120 caractères.

`scheduled_at: datetime | None = None` signifie que la date est soit un objet date-heure, soit absente. L’absence est autorisée par défaut.

```python
participants: list[ParticipantInput] = Field(min_length=1, max_length=30)
```

Cette ligne exige une liste contenant entre 1 et 30 objets participant valides.

La limite empêche de créer une réunion sans personne et réduit les abus d’envoi massif. Elle ne constitue pas à elle seule une protection complète contre le spam; il faudrait aussi limiter la fréquence des demandes.

### `class StartInput(BaseModel):`

Cette classe contient `notice_confirmed: bool`.

Le navigateur doit envoyer vrai pour déclarer que l’organisateur a annoncé aux personnes présentes que l’enregistrement va commencer.

Techniquement, le serveur enregistre une déclaration de l’organisateur. Il ne peut pas entendre ni prouver automatiquement que la phrase a réellement été prononcée.

## 6. Fonction `token_hash`

```python
def token_hash(token: str) -> str:
```

La fonction reçoit un texte nommé `token` et annonce qu’elle renvoie du texte.

```python
return hashlib.sha256(token.encode()).hexdigest()
```

Décomposition :

1. `token.encode()` transforme les caractères en octets, car SHA-256 travaille sur des octets ;
2. `hashlib.sha256(...)` calcule l’empreinte ;
3. `.hexdigest()` transforme les octets du résultat en caractères hexadécimaux faciles à stocker ;
4. `return` renvoie le texte obtenu.

La même entrée produit toujours la même empreinte. Une entrée différente produit normalement une empreinte très différente.

## 7. Fonction `owned_session`

```python
meeting = db.get(ConsentSession, session_id)
```

Cette ligne demande à la base la réunion dont la clé principale vaut `session_id`.

Une clé principale est l’identifiant unique d’une ligne.

```python
if not meeting or meeting.owner_id != user.id:
```

La condition est vraie si la réunion n’existe pas ou si son propriétaire n’est pas l’utilisateur connecté.

`or` signifie qu’une seule des deux situations suffit.

```python
raise HTTPException(404, "Réunion introuvable")
```

Le code 404 signifie « ressource introuvable ». Le même message est utilisé pour une réunion absente et une réunion appartenant à quelqu’un d’autre.

Ce choix évite de confirmer à un utilisateur qu’une réunion privée existe chez un autre compte.

```python
return meeting
```

Si les contrôles réussissent, la réunion autorisée est renvoyée.

Cette fonction évite de répéter le contrôle de propriété dans chaque route. C’est une application concrète de DRY.

## 8. Fonction `participants_for`

```python
select(ParticipantConsent).where(ParticipantConsent.session_id == session_id)
```

`select` demande des lignes de la table participant. `where` ajoute la condition : conserver uniquement celles dont l’identifiant de réunion correspond.

`db.exec(...)` exécute la requête. `list(...)` transforme le résultat en liste Python immédiatement utilisable plusieurs fois.

Sans filtre, la fonction mélangerait les participants de toutes les réunions, ce qui serait une grave fuite de données.

## 9. Fonction `is_active`

```python
return bool(consent.consented_at and not consent.withdrawn_at)
```

Un consentement est considéré actif si :

- une date d’acceptation existe ;
- aucune date de retrait n’existe.

`and` exige les deux conditions. `not` inverse la seconde. `bool` garantit un résultat strictement vrai ou faux.

Le code ne se contente donc pas d’un ancien accord : le retrait le désactive.

## 10. Fonction `refresh_status`

Cette fonction recalcule l’état global de la réunion.

```python
participants = participants_for(meeting.id, db)
```

Elle récupère la liste actuelle en base.

```python
if meeting.status != ConsentSessionStatus.RECORDING:
```

Elle ne remplace pas l’état pendant un enregistrement déjà actif.

Ensuite, l’expression conditionnelle donne `READY` si la liste n’est pas vide et si `all(...)` confirme que chaque participant est actif. Sinon, elle donne `PENDING`.

`all` parcourt toutes les valeurs et renvoie vrai uniquement si toutes sont vraies.

`db.add(meeting)` indique à la session SQLModel de suivre la réunion modifiée. Cette fonction ne fait pas elle-même `commit`; la route qui l’appelle valide ensuite l’ensemble de l’opération.

## 11. Fonction `session_detail`

Cette fonction transforme les objets de base en un dictionnaire pouvant être renvoyé au navigateur.

Les clés `id`, `title`, `scheduled_at`, `status` et `notice_confirmed_at` reprennent les informations de la réunion.

`all_consented` refait la vérification globale. `bool(participants)` empêche qu’une liste vide soit considérée comme « tout le monde a consenti ».

La clé `participants` contient une compréhension de liste. Pour chaque `item`, elle construit un dictionnaire limité à l’identifiant, au nom, au courriel et aux deux dates.

Cette sélection est importante : le serveur ne renvoie pas l’empreinte secrète du jeton.

## 12. Création de la réunion et des invitations

Le décorateur :

```python
@router.post("/consent-sessions", status_code=201)
```

relie une demande POST à la fonction. `201` signifie qu’une ressource a été créée.

### Paramètres injectés

`payload: SessionInput` est fabriqué à partir du JSON et validé.

`user: User = Depends(current_user)` demande à FastAPI d’appeler `current_user`. Si le jeton est invalide, la route ne continue pas.

`db: Session = Depends(get_session)` demande une session de base.

### Vérification SMTP

Si `settings.smtp_configured` est faux, le serveur renvoie 503. Ce code signifie que le service nécessaire est indisponible.

Le but est de ne pas créer silencieusement une réunion dont personne ne recevra les liens.

### Détection des doublons

```python
emails = [str(item.email).lower() for item in payload.participants]
```

Pour chaque participant, l’adresse validée est convertie en texte puis en minuscules.

```python
if len(emails) != len(set(emails)):
```

`len` compte les éléments. `set` fabrique un ensemble qui ne conserve qu’une fois chaque valeur.

Si le nombre diminue, au moins une adresse était répétée. Le serveur renvoie alors 400, c’est-à-dire une demande invalide.

### Création de l’objet réunion

`owner_id=user.id` attache la réunion au compte connecté.

`title=payload.title.strip()` retire les espaces inutiles au début et à la fin.

`scheduled_at` reprend la date facultative.

`db.add(meeting)` place l’objet dans la session. SQLModel fournit déjà son identifiant grâce au modèle.

### Liste `deliveries`

L’annotation `list[tuple[ParticipantInput, str]]` décrit une liste de paires. Chaque paire contiendra l’objet participant et son jeton réel.

Cette liste reste uniquement en mémoire le temps de la fonction. Elle n’est pas enregistrée dans la base.

### Boucle des participants

`for item in payload.participants` répète le bloc pour chaque personne.

```python
token = secrets.token_urlsafe(32)
```

Cette ligne fabrique une valeur aléatoire à partir de 32 octets, encodée avec des caractères sûrs dans une URL.

Le jeton réel sera mis dans le courriel. `token_hash(token)` enregistre seulement l’empreinte.

`notice_version=settings.privacy_version` mémorise la version de l’information liée à ce consentement.

`deliveries.append((item, token))` ajoute la paire à la liste d’envoi.

### Premier `db.commit()`

`commit` valide durablement la réunion et tous les participants dans la base.

Il a lieu avant l’envoi des courriels. Ainsi, un lien envoyé pointe déjà vers une ligne existante.

Conséquence : si un envoi échoue, la réunion et le participant restent en base. Le code collecte alors l’adresse dans `delivery_errors`, mais ne retente pas automatiquement.

### Envoi des mails

`failed: list[str] = []` crée la liste des adresses en échec.

La boucle essaie `send_consent_email`. Le bloc `try` entoure une action susceptible d’échouer. `except EmailError` capture l’erreur prévue et ajoute l’adresse à la liste.

Les autres types d’erreurs ne sont pas capturés par ce `except` et remontent.

Enfin, `session_detail` construit la réponse et la clé supplémentaire `delivery_errors` informe le frontend.

## 13. Démarrage de la réunion

L’adresse contient `{session_id}`. Les accolades indiquent une partie variable extraite de l’URL et transmise à la fonction.

`owned_session` vérifie immédiatement que la réunion appartient à l’utilisateur.

Si `notice_confirmed` est faux, la réponse 400 exige l’annonce aux personnes présentes.

Le serveur recharge les participants. S’il n’y en a aucun ou si un seul n’a pas d’accord actif, il renvoie 409. Le code 409 signale que la demande entre en conflit avec l’état actuel de la ressource.

Lorsque tout est bon :

- l’état devient `RECORDING`;
- `notice_confirmed_at` reçoit l’heure ;
- `started_at` reçoit l’heure ;
- la base est validée ;
- le détail mis à jour est renvoyé.

Les deux appels séparés à `utc_now()` peuvent différer de quelques microsecondes. Si l’on voulait strictement la même valeur, on la calculerait une fois dans une variable.

## 14. Arrêt par l’organisateur

La route `/stop` vérifie le propriétaire, place l’état à `STOPPED`, enregistre `stopped_at`, ajoute puis valide l’objet.

Elle ne vérifie pas que l’état précédent était `RECORDING`. Répéter l’appel réécrit simplement l’heure d’arrêt. L’opération n’est donc pas parfaitement idempotente concernant l’horodatage.

Idempotent signifie qu’une opération répétée produit le même état final observable. Un `DELETE` qui laisse la ressource absente est souvent conçu comme idempotent; ici l’heure change à chaque répétition.

## 15. Recherche d’un consentement public

`public_consent` reçoit le jeton visible dans l’URL.

Le serveur calcule son empreinte, cherche la première ligne correspondante avec `.first()` et renvoie 404 si rien n’est trouvé.

Le jeton agit ici comme un secret donnant accès aux actions du participant. Toute personne possédant le lien peut agir comme ce participant. Il ne doit donc pas apparaître dans des journaux publics ou être transféré sans contrôle.

Limite importante : dans ce commit, aucune date d’expiration du jeton n’est vérifiée. Le lien reste utilisable tant que la ligne et l’empreinte existent, sauf lorsque l’effacement remplace l’empreinte.

## 16. Lecture publique des informations

La route GET renvoie :

- le nom du participant ;
- le titre de la réunion ;
- les dates d’acceptation et de retrait ;
- la version de l’information ;
- le nom du sous-traitant Mistral ;
- le contact ;
- la durée de conservation annoncée.

`meeting.title if meeting else "Réunion"` est une expression conditionnelle : utiliser le vrai titre si la réunion existe, sinon un texte de secours.

La réponse ne renvoie pas l’adresse électronique.

## 17. Acceptation

La route recherche d’abord le consentement grâce au jeton.

```python
consent.consented_at = utc_now()
consent.withdrawn_at = None
```

La première ligne enregistre l’acceptation actuelle. La seconde efface un éventuel retrait précédent.

Cela signifie qu’un participant ayant refusé peut ensuite accepter avec le même lien. L’historique complet des changements n’est pas conservé : seules les dernières dates présentes dans la ligne le sont.

Le code recharge la réunion, ajoute le consentement et recalcule l’état si la réunion existe. Après `commit`, il renvoie l’état et la date.

Répéter l’acceptation modifie `consented_at`; cette route n’est donc pas strictement idempotente sur l’heure.

## 18. Retrait

Le retrait place `withdrawn_at` à l’heure actuelle.

Si la réunion existe, son état devient immédiatement `STOPPED` et une heure d’arrêt est enregistrée.

Cette règle traduit l’exigence : à tout moment, un participant peut retirer son accord et l’enregistrement doit s’arrêter.

Limite réelle : le backend change l’état en base, mais le microphone du navigateur ne s’arrête pas magiquement à cet instant. Le frontend organisateur doit surveiller cet état et arrêter ses pistes audio. Si le réseau est coupé ou si l’onglet ne vérifie plus, un délai ou un échec est possible.

## 19. Effacement

La route DELETE répond avec le code 204, ce qui signifie succès sans corps de réponse.

Elle trouve tous les liens entre la réunion du participant et les enregistrements.

Pour chaque lien :

1. elle charge l’enregistrement ;
2. elle calcule le chemin absolu ;
3. elle vérifie que le chemin déclaré existe, qu’il reste à l’intérieur du dossier audio autorisé et que le fichier existe ;
4. elle supprime le fichier avec `unlink` ;
5. elle cherche le rapport structuré associé ;
6. elle supprime le rapport s’il existe ;
7. elle supprime l’enregistrement ;
8. elle supprime le lien.

La vérification `path.is_relative_to(settings.audio_directory)` protège contre un chemin qui viserait un fichier en dehors du dossier autorisé. Sans elle, une valeur de base falsifiée pourrait conduire à supprimer un fichier arbitraire du serveur.

Ensuite, le nom devient `"Données effacées"`, le courriel devient vide, l’empreinte du jeton est remplacée par celle d’un nouveau jeton inconnu, et la date de demande est mémorisée.

La ligne de consentement est donc pseudonymisée plutôt que totalement supprimée. Une pseudonymisation remplace les identifiants directs, mais une donnée peut parfois rester rattachable avec d’autres informations. Ici, la réunion et certaines dates peuvent subsister.

Limite majeure : la demande d’un seul participant supprime tous les enregistrements et rapports liés à la réunion, donc aussi les données concernant les autres participants et l’organisateur. Cela peut être un choix prudent pour un enregistrement collectif indivisible, mais il doit être explicitement assumé dans les règles métier.

Autre limite : la route ne montre pas l’effacement d’éventuelles copies chez un prestataire déjà appelé, de sauvegardes ou de journaux. Une conformité réelle exige d’identifier tous les emplacements.

## 20. Les méthodes ajoutées dans `api.js`

Le fichier `api.js` centralise les demandes du frontend. `request` ajoute le jeton d’accès, choisit le type JSON, appelle `fetch`, transforme les erreurs et lit la réponse.

### `startConsentSession`

La fonction fléchée reçoit `id` et appelle l’adresse contenant cet identifiant.

Elle utilise POST et transforme `{ notice_confirmed: true }` en texte JSON grâce à `JSON.stringify`.

Le frontend envoie toujours vrai lorsqu’elle est appelée. La confirmation dépend donc du fait que l’interface appelle cette méthode seulement après une action claire de l’organisateur.

### `stopConsentSession`

Elle envoie POST sur `/stop`. Aucun corps n’est nécessaire.

### Méthodes publiques

`getPublicConsent(token)` effectue une lecture GET.

`acceptConsent` et `withdrawConsent` utilisent POST parce qu’elles modifient l’état.

`eraseConsentData` utilise DELETE.

Les littéraux entourés par des accents graves, comme `` `/api/public/consents/${token}` ``, sont des chaînes modèles JavaScript. `${token}` insère la valeur dans le texte.

Le jeton placé dans le chemin peut apparaître dans l’historique du navigateur et dans les journaux du serveur ou d’un proxy. Une conception plus forte peut utiliser un jeton court à durée limitée et des politiques de journalisation adaptées.

## 21. Le composant `PublicConsent`

### Signature

```jsx
export function PublicConsent({ token }) {
```

La fonction reçoit un objet de propriétés React. Les accolades dans le paramètre extraient directement la propriété `token`.

### Les trois états

`notice` contient les informations reçues, ou `null` avant le chargement.

`message` contient le message de réussite.

`error` contient le texte d’erreur.

`useState` renvoie une paire : la valeur actuelle et une fonction pour la remplacer. Par exemple `setError` demande à React de mémoriser une nouvelle erreur et de recalculer l’affichage.

### Chargement initial avec `useEffect`

`useEffect` demande d’exécuter un effet après l’affichage du composant. Un effet est une action extérieure au simple calcul visuel, ici une demande réseau.

`api.getPublicConsent(token)` renvoie une promesse. Une promesse représente un résultat disponible plus tard.

`.then(setNotice)` place la réponse dans l’état lorsqu’elle arrive.

`.catch(...)` place le message d’erreur si la demande échoue.

La liste `[token]` dit de refaire cet effet seulement si la valeur du jeton change.

En mode Strict de développement, React peut lancer, nettoyer puis relancer certains effets afin de révéler des problèmes. Un GET de lecture supporte normalement cette répétition.

### Fonction `act`

Cette fonction asynchrone reçoit une fonction d’action, par exemple `api.acceptConsent`.

Elle efface d’abord une ancienne erreur.

`await action(token)` attend la fin de la demande. `await` suspend cette fonction sans bloquer tout le navigateur.

`response?.status` utilise le chaînage optionnel : si `response` est absent, le résultat devient `undefined` au lieu de provoquer immédiatement une erreur.

L’opérateur conditionnel choisit le message d’acceptation si le statut vaut `accepted`, sinon le message de retrait.

Puis l’interface recharge l’information publique afin d’afficher l’état réel renvoyé par le serveur.

Le bloc `catch` transforme un échec en message visible.

### Affichages avant la page normale

Si une erreur existe et qu’aucune notice n’a jamais été reçue, le composant affiche uniquement l’erreur dans `PublicShell`.

Si la notice n’existe pas encore, il affiche « Chargement… ».

Ces `return` anticipés arrêtent la fonction avant le reste et simplifient les conditions.

### Calcul `active`

Il reprend la même règle que le backend : une date d’accord et aucune date de retrait.

Le frontend utilise ce résultat pour choisir les boutons, mais le backend reste la source de vérité. Un utilisateur peut modifier le JavaScript dans son navigateur; les contrôles importants doivent rester côté serveur.

### Contenu d’information

Les expressions entre accolades insèrent les données reçues dans le JSX.

La liste annonce :

- l’enregistrement de la voix ;
- la transmission à Mistral ;
- la transcription et la diarisation ;
- la création du résumé, des décisions et actions ;
- la suppression de l’audio ;
- la durée maximale des résultats ;
- les droits de retrait et d’effacement.

La diarisation consiste à séparer les prises de parole et à leur associer des intervenants ou des étiquettes. Dire que la diarisation est annoncée ne prouve pas sa précision; cela dépend du modèle et de la qualité audio.

### Affichage conditionnel des boutons

En JSX, `condition && élément` signifie « afficher l’élément uniquement si la condition est vraie ».

Si le consentement n’est pas actif, le bouton d’acceptation apparaît.

Le bouton « Je refuse » apparaît seulement avant un retrait déjà enregistré.

Si le consentement est actif, le bouton de retrait apparaît.

Chaque `onClick={() => act(...)}` fournit à React une fonction à lancer au clic. Sans la fonction fléchée, l’action serait appelée immédiatement pendant l’affichage.

### Effacement

Le gestionnaire de clic est asynchrone.

`confirm(...)` ouvre la boîte de confirmation native du navigateur. Si l’utilisateur annule, `return` arrête la fonction.

Après la demande DELETE, un message est affiché.

Limite : cette partie n’utilise pas `try/catch`. Si l’effacement échoue, le navigateur peut produire un rejet non géré et aucun message clair n’est posé dans `error`.

Autre limite : après effacement, le jeton devient invalide côté serveur mais la notice déjà en mémoire reste affichée jusqu’à un rechargement.

## 22. Le composant `PublicShell`

Cette petite fonction reçoit `children`.

`children` est le contenu placé entre `<PublicShell>` et `</PublicShell>`.

Elle centralise la structure de page, de carte et de marque. C’est DRY : les écrans d’erreur, de chargement, de consentement et d’information juridique utilisent le même cadre.

La fonction est compressée sur une ligne. Elle fonctionne mais une présentation sur plusieurs lignes serait plus facile à enseigner et à maintenir.

## 23. `LegalGate`

Ce composant concerne l’utilisateur inscrit dans Scribe, pas l’invité d’une réunion.

Il charge les mentions juridiques et exige deux cases séparées :

- acceptation des CGU ;
- reconnaissance de lecture de l’information RGPD.

Séparer les cases rend les deux actes plus explicites.

`termsChecked` et `privacyChecked` commencent à faux.

La demande `legalNotices` remplit `notice`. En cas d’échec, le message va dans `error`.

La fonction `accept` appelle le backend, puis `onAccepted`, fonction donnée par le composant parent afin de poursuivre l’application.

Les appels `.map((item) => <li key={item}>...)` transforment chaque texte d’une liste en élément visuel. `key` donne à React une identité stable pour comparer les éléments.

Le bouton est désactivé si `!termsChecked || !privacyChecked`, c’est-à-dire si au moins l’une des cases n’est pas cochée.

Limite juridique : le texte « reconnaissance de lecture » n’est pas forcément un consentement au traitement. Selon le traitement, la base légale peut être le contrat, une obligation ou un intérêt légitime. Le code affiche les bases fournies par le backend, mais leur exactitude doit être validée.

## 24. Ce que ce système garantit réellement

Il garantit au niveau applicatif que :

- un organisateur connecté ne peut agir que sur ses réunions par ces routes ;
- un lien public doit correspondre à une empreinte connue ;
- le démarrage est refusé tant qu’un consentement manque ;
- un retrait arrête l’état serveur ;
- une date de consentement et une version d’information sont conservées ;
- une demande d’effacement supprime les enregistrements et rapports retrouvés pour la réunion.

Il ne garantit pas à lui seul que :

- la personne ayant le lien est vraiment celle dont le nom est affiché ;
- le lien expire ;
- le microphone s’arrête instantanément en cas de réseau coupé ;
- tous les prestataires et sauvegardes ont effacé leurs copies ;
- le texte juridique est suffisant ;
- le consentement était réellement libre dans le contexte professionnel ;
- les envois de courriel seront toujours livrés ;
- la durée de conservation de 30 jours est automatiquement appliquée.

## 25. Réponse orale de Yanis

« Pour chaque participant, le backend génère un jeton aléatoire avec le module `secrets`, envoie le jeton dans le lien et ne garde en base que son empreinte SHA-256. La page publique présente le traitement puis appelle les routes d’acceptation, de retrait ou d’effacement. Un consentement actif exige une date d’acceptation et aucune date de retrait. Le démarrage vérifie à nouveau cette règle côté backend pour tous les participants et exige aussi la confirmation de l’annonce sur place. Un retrait place immédiatement la réunion à l’état arrêté; le frontend doit surveiller cet état pour couper les pistes du microphone. Je connais les limites : le jeton n’expire pas encore, l’effacement collectif doit être assumé, et la durée de conservation annoncée nécessite une tâche automatique supplémentaire. »

## 26. Questions pièges

**Pourquoi ne pas stocker le jeton en clair ?**  
Parce qu’une lecture de la base donnerait directement des liens utilisables. L’empreinte permet la comparaison sans conserver le secret original.

**SHA-256 chiffre-t-il le jeton ?**  
Non. Il le hache. Il n’existe pas de clé de déchiffrement.

**Une adresse validée avec `EmailStr` existe-t-elle forcément ?**  
Non. Sa forme est valide, mais seul l’envoi ou un mécanisme de confirmation peut vérifier l’accès à la boîte.

**Pourquoi un contrôle dans le frontend et dans le backend ?**  
Le frontend guide l’utilisateur; il peut être modifié localement. Le backend applique la vraie règle de sécurité.

**Que signifie 409 ?**  
La demande est comprise, mais elle est incompatible avec l’état actuel : tous les participants n’ont pas encore consenti.

**Le retrait arrête-t-il physiquement le micro ?**  
Il arrête l’état serveur. Le navigateur organisateur doit détecter le changement et arrêter ses pistes. Sans réseau, il existe une limite technique.

**Le consentement est-il idempotent ?**  
Le résultat logique « accepté » peut être le même, mais l’heure est réécrite à chaque appel; la réponse exacte change donc.

**Pourquoi conserver une ligne après l’effacement ?**  
Pour mémoriser qu’une demande d’effacement a existé sans garder le nom et le courriel. Il faut toutefois vérifier que les données restantes sont réellement nécessaires et suffisamment anonymisées.

