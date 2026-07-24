# Yanis — l’envoi sécurisé de l’audio expliqué depuis zéro

Ce chapitre explique le commit :

- [`2a1dbd0 — feat(recording): add secure audio upload`](https://github.com/AshDv/ScribeProject/commit/2a1dbd0cc227d07739776329f5f517473913f15c)

Le mot `feat` annonce une fonctionnalité. `recording` indique qu’elle concerne les enregistrements. `add secure audio upload` signifie « ajouter l’envoi contrôlé d’un fichier audio ».

« Sécurisé » ne veut pas dire « impossible à attaquer ». Ici, cela signifie que le code contrôle l’utilisateur, la réunion, les consentements, le type déclaré, la taille, le chemin de stockage et la propriété lors de la lecture ou suppression.

## 1. Ce qu’est un upload

Un upload est le transfert d’un fichier depuis l’appareil de l’utilisateur vers le serveur.

Dans Scribe, le navigateur enregistre le microphone, fabrique un objet audio, puis envoie cet objet à la route `POST /api/recordings`.

Le serveur ne reçoit pas seulement du JSON. Il reçoit un formulaire `multipart/form-data`, format HTTP capable de transporter plusieurs champs texte et un fichier binaire dans la même demande.

« Binaire » signifie que le contenu est constitué d’octets qui ne représentent pas directement un texte lisible.

## 2. Les nouveaux imports

### `import json`

Le module `json` transforme une chaîne JSON en objets Python. Il sert à relire les champs structurés enregistrés sous forme de texte.

### `from pathlib import Path`

`Path` sert à manipuler et vérifier le chemin du fichier audio lors de la suppression.

### `BackgroundTasks`

FastAPI fournit `BackgroundTasks` pour programmer une fonction juste après l’envoi de la réponse.

Ici, le serveur peut répondre « enregistrement accepté » sans attendre toute la transcription et le résumé.

Limite importante : ce travail reste dans le même processus FastAPI. Si le processus s’arrête, la tâche peut être perdue. Ce n’est pas une file de travaux durable et ce n’est pas une architecture serverless robuste.

### `File`, `Form` et `UploadFile`

`File` dit qu’un paramètre vient de la partie fichier du formulaire.

`Form` dit qu’un paramètre vient d’un champ texte du formulaire.

`UploadFile` est l’objet représentant le fichier reçu : nom annoncé, type annoncé et flux de contenu.

### `StructuredReport` et `SessionRecording`

`StructuredReport` représente le résultat détaillé du LLM.

`SessionRecording` représente une table de liaison. Une table de liaison relie deux objets sans recopier toutes leurs colonnes : ici une réunion de consentement et un enregistrement.

### `process_recording`

Cette fonction sera appelée en arrière-plan pour transcrire et résumer le fichier.

À la date de ce commit, son comportement final dépend des commits suivants. Le fait de l’appeler ici établit seulement le passage entre l’envoi et le traitement.

## 3. La constante `ALLOWED_AUDIO`

```python
ALLOWED_AUDIO = {
    "audio/webm": ".webm",
    "audio/wav": ".wav",
    "audio/x-wav": ".wav",
    "audio/mpeg": ".mp3",
    "audio/mp4": ".m4a",
    "audio/x-m4a": ".m4a",
}
```

Une constante est une variable que l’équipe a l’intention de ne pas modifier pendant l’exécution. Python ne l’interdit pas, mais les majuscules signalent cette intention.

Les accolades créent un dictionnaire. La clé à gauche est un type MIME annoncé par le navigateur. Un type MIME est un texte standard décrivant le format d’un contenu transmis sur le Web.

La valeur à droite est l’extension choisie pour le fichier stocké.

Les variantes `audio/wav` et `audio/x-wav` conduisent toutes deux à `.wav`. De même pour M4A.

Le dictionnaire permet à la fois de refuser les types inconnus et de choisir une extension maîtrisée. Le serveur n’utilise pas directement le nom de fichier fourni par l’utilisateur, ce qui évite qu’un nom contienne un chemin malveillant.

Limite : `audio.content_type` vient de la demande du client. Une personne peut mentir sur cette valeur. Pour une vérification plus forte, le serveur devrait inspecter la signature réelle du fichier ou essayer de le décoder dans un environnement contrôlé.

## 4. `CONSENT_VERSION`

```python
CONSENT_VERSION = "2026-07-26"
```

Cette constante associe l’enregistrement à une version de consentement.

La valeur est une chaîne de caractères qui ressemble à une date. Elle ne vérifie pas automatiquement le contenu exact de l’information montrée. Idéalement, elle devrait être reliée à la même source de version que les mentions juridiques, pour éviter deux dates contradictoires.

## 5. Fonction `owned_recording`

```python
def owned_recording(recording_id: str, user: User, session: Session) -> Recording:
```

La fonction reçoit :

- l’identifiant de l’enregistrement demandé ;
- l’utilisateur connecté ;
- la session de base.

Elle annonce qu’elle renvoie un objet `Recording`.

```python
recording = session.get(Recording, recording_id)
```

Cette ligne cherche la ligne par sa clé principale.

```python
if not recording or recording.owner_id != user.id:
```

La demande est refusée si l’enregistrement n’existe pas ou appartient à un autre compte.

```python
raise HTTPException(404, "Enregistrement introuvable")
```

Le même 404 masque l’existence d’une ressource étrangère.

```python
return recording
```

La fonction ne rend l’objet que lorsque le contrôle de propriété a réussi.

Cette fonction est utilisée par la lecture et la suppression. Centraliser le contrôle évite qu’une route oublie une condition.

## 6. Fonction `parse_json`

```python
def parse_json(value: str | None) -> list:
    return json.loads(value) if value else []
```

La fonction reçoit du texte JSON ou aucune valeur. Elle annonce une liste.

Si `value` existe, `json.loads` analyse le texte et le transforme en objet Python. Sinon, une liste vide est renvoyée.

Exemple : le texte `'["budget", "planning"]'` devient une vraie liste Python contenant deux textes.

Limites :

- l’annotation annonce toujours une liste, mais un texte JSON pourrait contenir un dictionnaire ;
- si le texte est invalide, `json.loads` déclenche une erreur non capturée ;
- enregistrer du JSON dans des colonnes texte est simple pour le MVP mais moins pratique pour rechercher ou valider les éléments en base.

## 7. Fonction `recording_detail`

Cette fonction prépare la réponse complète d’un enregistrement.

### Paramètre facultatif `session`

`session: Session | None = None` signifie que l’appelant peut fournir une session ou ne rien fournir.

Si elle est fournie, la fonction cherche aussi le rapport structuré. Sinon `report` devient `None`.

### Recherche du rapport

La requête sélectionne `StructuredReport` là où `recording_id` correspond à l’enregistrement, puis prend la première ligne.

L’expression est écrite avec une condition `if session else None`. Elle évite une requête lorsque la session manque.

### Dictionnaire `result`

Chaque clé expose une information précise :

- `id` : identifiant unique ;
- `title` : titre donné par l’utilisateur ;
- `status` : état du traitement ;
- `created_at` : création ;
- `completed_at` : fin ;
- `error` : message d’échec éventuel ;
- `transcript` : texte de la réunion ;
- `segments` : prises de parole structurées ;
- `summary` : résumé ;
- `topics` : thèmes ;
- `decisions` : décisions ;
- `actions` : actions ;
- `consent_version` : version de l’accord associé.

Les champs JSON sont transformés avec `parse_json` avant d’être envoyés.

### Partie `if report`

Si un rapport détaillé existe, une clé `report` est ajoutée.

Elle contient le nom du modèle, la langue, le procès-verbal détaillé, les intervenants, points clés, décisions, actions, questions, risques et mesure de couverture.

Cette fonction choisit explicitement ce que l’API expose. Elle ne renvoie pas `audio_path`, ce qui évite de révéler le chemin local du serveur.

## 8. Le décorateur de création

```python
@router.post("/recordings", status_code=202)
```

La méthode POST crée un traitement.

Le code 202 signifie « demande acceptée pour traitement », mais résultat pas encore terminé. C’est plus honnête qu’un code 200 qui pourrait laisser croire que le compte rendu est déjà prêt.

## 9. Signature de `create_recording`

La fonction est `async` parce qu’elle attend la lecture du fichier avec `await`.

`background_tasks: BackgroundTasks` est fourni automatiquement par FastAPI.

```python
title: str = Form(..., min_length=1, max_length=120)
```

Le titre vient du formulaire. Les trois points `...` signifient « obligatoire ». Sa longueur est limitée.

```python
consent: bool = Form(...)
```

Ce booléen représente la confirmation de l’utilisateur qui actionne le dictaphone.

```python
consent_session_id: str = Form(...)
```

Ce texte relie le fichier à la réunion dont les participants ont été invités.

```python
audio: UploadFile = File(...)
```

Le fichier audio est obligatoire.

`user` et `session` sont fournis par les dépendances d’authentification et de base.

## 10. Première barrière : confirmation locale

```python
if not consent:
    raise HTTPException(400, "Votre consentement est obligatoire")
```

Si le booléen est faux, le fichier est refusé.

Ce contrôle ne remplace pas les consentements participants. Il représente une couche supplémentaire pour la personne qui démarre l’enregistrement en présentiel.

## 11. Deuxième barrière : propriété de la réunion

Le serveur charge `ConsentSession` avec l’identifiant reçu.

Si elle n’existe pas ou appartient à un autre utilisateur, il renvoie 404.

Cela empêche un compte d’attacher son audio à la réunion privée d’un autre compte.

## 12. Troisième barrière : état `RECORDING`

Si l’état n’est pas `RECORDING`, la réponse 409 refuse l’envoi.

Pour atteindre cet état, la route de démarrage a déjà exigé tous les consentements et l’annonce sur place.

Ce contrôle reste nécessaire parce qu’un utilisateur peut appeler directement l’API sans suivre l’interface.

## 13. Quatrième barrière : nouvelle vérification des participants

Le serveur relit tous les participants au moment exact de l’upload.

La condition exige au moins un participant et utilise `all` sur :

```python
item.consented_at and not item.withdrawn_at
```

Cette deuxième vérification est essentielle : un participant peut avoir retiré son consentement après le démarrage.

Il existe encore une fenêtre de temps entre cette vérification et l’écriture du fichier. Une transaction ou une règle de verrouillage plus poussée serait nécessaire pour éliminer toutes les courses entre deux demandes simultanées.

Une course, ou race condition, se produit lorsque le résultat dépend de l’ordre imprévisible de deux actions concurrentes.

## 14. Vérification du type annoncé

```python
content_type = (audio.content_type or "").split(";")[0].lower()
```

Décomposition :

1. prendre le type annoncé, ou un texte vide s’il manque ;
2. couper au point-virgule afin d’ignorer un éventuel paramètre ;
3. garder la première partie ;
4. convertir en minuscules.

```python
extension = ALLOWED_AUDIO.get(content_type)
```

`.get` cherche la clé dans le dictionnaire. Si elle manque, le résultat est `None` au lieu d’une erreur.

Si aucune extension n’est trouvée, le serveur renvoie 415. Ce code signifie « type de média non pris en charge ».

## 15. Lecture avec une limite

```python
data = await audio.read(settings.max_audio_mb * 1024 * 1024 + 1)
```

Un mégaoctet est calculé ici comme 1024 × 1024 octets.

Le serveur demande au maximum la limite plus un octet. Cet octet supplémentaire permet de savoir si le fichier dépasse la limite sans lire volontairement une quantité illimitée.

Si `data` est vide, la réponse 400 signale un fichier vide.

Si la longueur dépasse la limite exacte, la réponse 413 signale une charge trop grande.

Conséquence mémoire : tout le fichier autorisé, jusqu’à environ 50 Mo, est placé dans la mémoire vive du processus. Plusieurs uploads simultanés peuvent donc consommer beaucoup de mémoire. Une version de production devrait lire par morceaux et compter la taille progressivement.

## 16. Création du dossier

`mkdir(parents=True, exist_ok=True)` crée le dossier et ses parents manquants, sans échouer s’il existe.

Comme ce travail est déjà effectué au démarrage, cette ligne est une sécurité supplémentaire. Elle est idempotente concernant l’existence du dossier.

## 17. Création de l’objet `Recording`

`owner_id=user.id` enregistre le propriétaire.

`title=title.strip()` nettoie les espaces extérieurs.

```python
original_filename=f"recording{extension}"
```

Le nom original donné par le navigateur n’est pas conservé. Le serveur construit un nom neutre à partir de l’extension autorisée.

Cela réduit les données conservées et évite les caractères dangereux dans un nom fourni par l’utilisateur. En revanche, le nom de colonne `original_filename` devient un peu trompeur, car la valeur n’est pas réellement le nom original.

`content_type` conserve le type normalisé.

`audio_path=""` commence vide parce que le chemin dépend de l’identifiant généré lors de la création de l’objet.

`consent_version` conserve la constante.

## 18. Fabrication et écriture du chemin

```python
path = settings.audio_directory / f"{recording.id}{extension}"
```

L’opérateur `/` entre deux objets `Path` assemble le dossier et le nom.

Le nom utilise l’identifiant généré par le serveur, pas une entrée utilisateur. Cela empêche une attaque de traversée de chemin où un nom comme `../../secret` viserait un autre dossier.

```python
path.write_bytes(data)
```

Cette ligne écrit tous les octets sur le disque.

Si un fichier du même nom existait, il serait remplacé. Les identifiants aléatoires rendent une collision très improbable, mais le code ne demande pas explicitement une création exclusive.

```python
recording.audio_path = str(path)
```

Le chemin est transformé en texte puis placé dans l’objet destiné à la base.

## 19. Enregistrement en base

`session.add(recording)` ajoute l’enregistrement.

`SessionRecording(...)` crée la ligne de liaison entre la réunion et l’enregistrement.

`session.commit()` valide les deux lignes ensemble dans la transaction courante. Une transaction regroupe des opérations de base qui doivent réussir ensemble.

`session.refresh(recording)` relit l’objet depuis la base pour obtenir ses valeurs finales.

Limite de cohérence : le fichier disque est écrit avant le commit. Si le commit échoue, un fichier peut rester sans ligne de base. À l’inverse, une stratégie écrivant après le commit peut laisser une ligne sans fichier si l’écriture échoue. Une version robuste doit prévoir un nettoyage compensatoire.

## 20. Lancement du traitement

```python
background_tasks.add_task(process_recording, recording.id)
```

La fonction `process_recording` et l’identifiant sont enregistrés comme tâche à exécuter après la réponse.

Le code ne crée pas un nouveau service indépendant. La tâche utilise le même serveur et le même disque.

En cas de redémarrage entre la réponse et la fin, rien dans cette ligne ne garantit une reprise. Pour la production, une file durable avec reprise, nombre de tentatives et identifiant idempotent serait plus sûre.

La route renvoie immédiatement `recording_detail`. L’état initial devrait être `UPLOADED` selon le modèle.

## 21. Liste des enregistrements

La route GET exige l’utilisateur connecté.

La requête filtre sur `Recording.owner_id == user.id`, puis trie par date décroissante grâce à `.desc()`.

`.all()` récupère toutes les lignes correspondantes.

La compréhension de liste renvoie seulement quatre champs par enregistrement. La liste reste légère; le détail complet est demandé séparément.

Limite : aucune pagination n’est prévue. Une pagination renvoie par exemple 20 éléments puis permet de demander la page suivante. Sans elle, un compte possédant des milliers d’enregistrements reçoit tout en une fois.

## 22. Lecture d’un enregistrement

La route contient l’identifiant dans l’URL.

`owned_recording` vérifie la propriété, puis `recording_detail` prépare la réponse complète avec le rapport.

Le contrôle est côté backend. Cacher un bouton frontend ne serait pas une protection suffisante.

## 23. Suppression d’un enregistrement

La route DELETE renvoie 204.

Elle commence par le contrôle de propriété.

Elle cherche puis supprime la ligne de liaison `SessionRecording`.

Elle cherche puis supprime le `StructuredReport`.

Ensuite :

```python
path = Path(recording.audio_path).resolve()
```

Le chemin stocké devient absolu.

```python
if path.is_relative_to(settings.audio_directory) and path.exists():
    path.unlink()
```

Le fichier est supprimé seulement s’il se trouve sous le dossier audio autorisé et s’il existe.

Cette vérification évite de supprimer un autre fichier du système si une valeur incorrecte est présente en base.

Puis la ligne `Recording` est supprimée et `commit` valide les changements.

Limites :

- `Path("").resolve()` devient le dossier courant si le chemin est vide ; la condition de parenté évite généralement l’effacement, mais une vérification explicite de chaîne vide serait plus claire ;
- le fichier est supprimé avant le commit ; si le commit échoue, la base peut encore référencer un fichier disparu ;
- aucune copie éventuellement transmise à un fournisseur n’est traitée ici ;
- un rapport déjà exporté ailleurs n’est pas retrouvé par cette fonction.

## 24. Pourquoi le fichier s’appelle `routes.py`

Une route relie une méthode HTTP et une adresse à une fonction Python.

À ce stade, `routes.py` contient aussi l’authentification, le SSO et les enregistrements. C’est simple pour un petit MVP, mais le fichier grandit.

KISS ne signifie pas tout placer dans un seul fichier. Lorsque plusieurs domaines deviennent difficiles à parcourir, séparer `auth_routes.py` et `recording_routes.py` peut devenir plus simple, à condition de ne pas créer une architecture inutilement complexe.

## 25. Sécurité : ce que fait chaque contrôle

Le jeton d’accès prouve l’authentification déclarée du compte.

`owner_id` contrôle l’autorisation : être connecté ne suffit pas, il faut posséder la ressource.

L’état de réunion contrôle le processus métier.

Les dates de consentement contrôlent la règle RGPD définie par l’application.

Le dictionnaire MIME limite les formats déclarés.

La lecture bornée limite la taille mémoire par demande.

L’identifiant généré empêche d’utiliser un nom de fichier utilisateur comme chemin.

`is_relative_to` limite l’emplacement pouvant être supprimé.

Aucun de ces contrôles ne remplace les autres.

## 26. Réponse orale de Yanis

« La route reçoit un formulaire contenant le titre, la confirmation, l’identifiant de réunion et le fichier. Avant d’écrire quoi que ce soit, elle vérifie l’utilisateur, la propriété de la réunion, l’état `RECORDING` et tous les consentements actifs. Elle normalise le type MIME, le compare à une liste autorisée et lit au maximum la taille prévue plus un octet. Le nom stocké est fabriqué avec l’identifiant serveur, jamais avec le nom envoyé par le client. La base relie ensuite l’enregistrement à la réunion et une tâche FastAPI lance le traitement après la réponse 202. Je sais que cette tâche et ce disque local ne sont pas durables en production, que le MIME client doit être vérifié par le contenu et que la lecture complète en mémoire doit devenir un flux par morceaux. »

## 27. Questions pièges

**Pourquoi le code lit-il la limite plus un octet ?**  
Pour détecter un dépassement sans lire volontairement un fichier entier de taille inconnue.

**Le type MIME garantit-il un vrai audio ?**  
Non. Il est annoncé par le client. Une inspection du contenu est nécessaire pour une garantie plus forte.

**Pourquoi ne pas conserver le nom original ?**  
Pour réduire les données inutiles et éviter qu’un texte contrôlé par l’utilisateur devienne un chemin.

**Quelle différence entre authentification et autorisation ?**  
L’authentification répond « qui est connecté ? ». L’autorisation répond « cette personne a-t-elle le droit d’accéder à cet enregistrement ? ».

**Pourquoi 202 au lieu de 200 ?**  
Parce que le fichier est accepté mais la transcription et le résumé ne sont pas encore terminés.

**La tâche d’arrière-plan est-elle un serveur séparé ?**  
Non. Elle s’exécute dans le processus FastAPI après la réponse et peut être perdue lors d’un arrêt.

**Le système est-il serverless à ce stade ?**  
Non. Le fichier SQLite, le disque local et la tâche en processus supposent un serveur local durable. Ce MVP doit être adapté pour une architecture serverless.

**Que veut dire « transaction » ?**  
C’est un groupe d’opérations de base validées ensemble par `commit`. Elle ne couvre pas automatiquement le fichier disque.

