# Code review S1 — Yanis Zedira

Version étudiée : branche `develop`, commit final `9040eef` après la PR #16.  
Périmètre personnel : 10 commits signés `Yanis Zedira <myanis.zedira@gmail.com>`.

> **Nouveau point de départ recommandé :**
> [le guide zéro jargon, commit par commit et ligne par ligne](yanis-zero-to-expert/00-commencer-ici.md).
> Il définit chaque mot avant de l’utiliser, traduit les signes du code et explique les effets, les
> raisons, les pannes possibles et les limites sans supposer de connaissances en informatique.

> Pour la lecture strictement commit → fichier → lignes, ouvrir
> [l’annexe ligne par ligne](yanis-line-by-line/00-index.md).

## Navigation rapide du manuel maximal

- Sections 1 à 10 : revue fonctionnelle des dix commits.
- Sections 11 à 20 : fondamentaux de programmation, stack, API, SQL, IA et Git.
- Sections 21 à 30 : lecture ligne par ligne de chaque commit.
- Section 31 : liens GitHub exacts à ouvrir pendant la soutenance.
- Sections 33 et 34 : questions du professeur et questions agressives.
- Section 35 : défauts classés par priorité.
- Sections 36 et 37 : tests à proposer et exercices oraux.
- Sections 40 et 41 : pitch complet et fiche de dernière révision.
- Sections 42 à 47 : localhost, ports, réseau, idempotence, transactions, concurrence et fiabilité.

Le code étudié est celui réellement présent dans Git. Lorsqu’une limite est mentionnée, il faut la
reconnaître : inventer une garantie est plus dangereux devant le jury que présenter une correction
précise.

## 1. Ce que Yanis a réellement réalisé

Yanis a travaillé sur quatre ensembles cohérents :

1. La fondation du backend et du frontend.
2. Le consentement public, son retrait et l’effacement.
3. Le téléversement audio et le dictaphone du navigateur.
4. La génération puis le stockage du compte rendu avec Mistral.

Il ne faut pas revendiquer les modèles SQL, l’authentification ou la transcription Voxtral comme des travaux entièrement personnels. Ces briques viennent respectivement d’Ashwin ou d’Aymen, mais le code de Yanis les utilise et les relie.

## 2. Les 10 commits, les PR et les responsabilités

| # | Commit | PR | Responsabilité |
|---|---|---|---|
| 1 | [2646623 — backend configuration](https://github.com/AshDv/ScribeProject/commit/2646623fc7c4bf83106cc4629ffa934131303012) | [PR #3](https://github.com/AshDv/ScribeProject/pull/3) | Configuration, dépendances, secrets ignorés et script de lancement |
| 2 | [452b4ff — database and health endpoint](https://github.com/AshDv/ScribeProject/commit/452b4ff60921cba714272cecdb51713c3d65385a) | [PR #3](https://github.com/AshDv/ScribeProject/pull/3) | Connexion SQLModel, cycle de vie FastAPI et contrôle de santé |
| 3 | [ed08945 — frontend tooling](https://github.com/AshDv/ScribeProject/commit/ed08945d27613f7d2942baf3e482465483e338bb) | [PR #3](https://github.com/AshDv/ScribeProject/pull/3) | React, Vite, point d’entrée et proxy vers l’API |
| 4 | [6104ac5 — application shell](https://github.com/AshDv/ScribeProject/commit/6104ac55c5dad4fe4b6d7382a7ea5d17c9862250) | [PR #3](https://github.com/AshDv/ScribeProject/pull/3) | Première page et système visuel responsive |
| 5 | [4e21df6 — consent acceptance and withdrawal](https://github.com/AshDv/ScribeProject/commit/4e21df68d3c0241f1ca5d9b9751e8aeaf5315daa) | [PR #10](https://github.com/AshDv/ScribeProject/pull/10) | Blocage serveur, accord, retrait, arrêt et effacement |
| 6 | [ecd894c — public consent page](https://github.com/AshDv/ScribeProject/commit/ecd894ce955b396193fcc1300278517fbd4c3d35) | [PR #10](https://github.com/AshDv/ScribeProject/pull/10) | Interface publique de consentement et appels API associés |
| 7 | [2a1dbd0 — secure audio upload](https://github.com/AshDv/ScribeProject/commit/2a1dbd0cc227d07739776329f5f517473913f15c) | [PR #11](https://github.com/AshDv/ScribeProject/pull/11) | Contrôles serveur, stockage temporaire et endpoints des enregistrements |
| 8 | [1ae2765 — browser dictaphone](https://github.com/AshDv/ScribeProject/commit/1ae2765b1bb0b9d585757c781a44ff2f4fc5b428) | [PR #11](https://github.com/AshDv/ScribeProject/pull/11) | MediaRecorder, états du dictaphone et surveillance du consentement |
| 9 | [1f88e83 — structured meeting reports](https://github.com/AshDv/ScribeProject/commit/1f88e83fc774214614d25ddcfb07ea9ae989a4f1) | [PR #14](https://github.com/AshDv/ScribeProject/pull/14) | Schéma du compte rendu, prompt et appel Mistral |
| 10 | [15511bd — transcription and summary pipeline](https://github.com/AshDv/ScribeProject/commit/15511bdaf809f905b2a76ab273e9f2f2be256469) | [PR #14](https://github.com/AshDv/ScribeProject/pull/14) | Enchaînement Voxtral/Mistral, persistance et suppression de l’audio |

Répartition des lignes : le commit frontend `ed08945` semble volumineux parce que `package-lock.json` contient environ 1 800 lignes générées automatiquement par npm. Ce fichier n’est pas du code métier écrit manuellement ; il verrouille exactement les dépendances indirectes pour rendre les installations reproductibles.

## 3. Architecture complète à savoir réciter

```text
Navigateur React
    |
    | HTTP /api + JWT
    v
FastAPI
    |
    +-- SQLModel --> SQLite locale
    |
    +-- fichier audio temporaire
    |
    +-- Voxtral --> transcription + segments + intervenants
    |
    +-- Mistral Medium 3.5 --> compte rendu JSON validé
    |
    +-- SQLite --> transcription et compte rendu
    |
    `-- suppression du fichier audio
```

Le frontend n’accède jamais directement à SQLite ou à Mistral. Toutes les règles importantes sont revérifiées par le backend, car le navigateur ne doit jamais être considéré comme fiable.

---

# COMMIT 1 — Configuration du backend

[Voir le commit 2646623](https://github.com/AshDv/ScribeProject/commit/2646623fc7c4bf83106cc4629ffa934131303012)

## Objectif

Créer une configuration unique et typée pour éviter de disperser des valeurs ou des secrets dans le code. Préparer également un lancement local reproductible.

## Fichiers importants

- `.gitignore`
- `pyproject.toml`
- `server/.env.example`
- `server/app/config.py`
- `server/requirements.txt`
- `server/app/processing.py`
- `start.ps1`

## `Settings` et Pydantic

`Settings` hérite de `BaseSettings`. Pydantic lit les variables d’environnement et le fichier `.env`, convertit les valeurs dans le bon type et applique les valeurs par défaut.

Exemples :

- `smtp_port: int` transforme la valeur texte en nombre.
- `smtp_use_tls: bool` transforme `true` en booléen.
- `mistral_api_key: str | None` rend la clé facultative au démarrage.
- `max_audio_mb: int` centralise la limite d’un fichier.

`extra="ignore"` signifie que d’anciennes variables peuvent rester dans le `.env` sans empêcher le serveur de démarrer.

## Pourquoi `@lru_cache`

`get_settings()` est mis en cache pour construire une seule instance de configuration. Les modules partagent donc les mêmes réglages et ne relisent pas le disque à chaque requête.

Conséquence à connaître : une modification du `.env` demande un redémarrage du backend.

## Propriétés calculées

- `cors_list` transforme une chaîne séparée par des virgules en liste.
- `audio_directory` transforme le chemin audio en chemin absolu.
- `google_sso_configured` vérifie la présence du client et du secret Google.
- `smtp_configured` vérifie une configuration minimale d’e-mail.
- `legal_configured` vérifie que l’identité juridique n’est pas restée vide.

## Secrets et `.gitignore`

`.env`, les bases SQLite, `server/data`, les environnements Python et `node_modules` sont ignorés. `.env.example` reste volontairement versionné, car il ne contient que les noms des variables et des valeurs fictives.

Réponse orale :

> Le dépôt contient le contrat de configuration, jamais les valeurs secrètes. Les valeurs réelles sont injectées localement ou par le gestionnaire de secrets de l’hébergeur.

## Dépendances

Les versions Python sont fixées avec `==` afin que deux développeurs installent les mêmes versions. Ruff vérifie le style et les erreurs statiques. Pytest exécute les tests.

`pyproject.toml` fixe :

- Python 3.12 comme cible ;
- une longueur de ligne de 100 caractères ;
- les familles de règles Ruff ;
- `server/tests` comme dossier de tests.

`B008` est ignorée parce que FastAPI utilise volontairement `Depends(...)` comme valeur par défaut dans les signatures.

## `start.ps1`

Le script :

1. crée l’environnement Python si nécessaire ;
2. installe les dépendances ;
3. crée `.env` depuis l’exemple s’il manque ;
4. installe les dépendances frontend ;
5. lance FastAPI sur `8000` ;
6. lance Vite sur `5174` ;
7. ouvre le navigateur.

## Limites à reconnaître

- La valeur par défaut de `SECRET_KEY` ne doit jamais être utilisée en production.
- `smtp_configured` ne teste pas réellement la connexion SMTP. C’est la raison pour laquelle une configuration peut sembler présente alors que le port 587 est bloqué.
- `start.ps1` est un outil Windows de développement, pas un script de production.
- Il utilise `npm install`; `npm ci` serait plus strict avec le lockfile.
- Il ne vérifie pas encore la version minimale de Node, ce qui a produit l’erreur Vite avec Node 20.11.
- Les dépendances de développement et de production sont dans le même fichier Python.

## Questions probables

**Pourquoi ne pas mettre la clé Mistral directement dans le code ?**  
Parce qu’un secret versionné reste dans l’historique Git, même après suppression. Il doit vivre dans `.env` en local et dans un coffre de secrets en production.

**Pourquoi typer les réglages ?**  
Pour détecter tôt une mauvaise valeur et éviter de convertir les chaînes dans chaque fonction.

**Pourquoi un `.env.example` ?**  
Il documente les variables obligatoires sans révéler les vraies valeurs.

---

# COMMIT 2 — Base de données et démarrage FastAPI

[Voir le commit 452b4ff](https://github.com/AshDv/ScribeProject/commit/452b4ff60921cba714272cecdb51713c3d65385a)

## Objectif

Fournir une connexion SQLModel commune, une session par requête et un cycle de démarrage propre.

## Le moteur SQLModel

`create_engine(settings.database_url)` construit le moteur SQLAlchemy utilisé par SQLModel.

Pour SQLite :

```python
{"check_same_thread": False}
```

FastAPI peut exécuter des requêtes dans différents threads. Ce réglage autorise l’utilisation de la connexion SQLite dans ce contexte. Il ne transforme pas SQLite en base distribuée et ne règle pas les limites de concurrence d’une production multi-instance.

## `init_db`

La fonction importe les modèles puis appelle `SQLModel.metadata.create_all(engine)`. L’import est nécessaire pour que les tables soient connues dans les métadonnées.

`create_all` crée les tables manquantes, mais ne remplace pas un système de migrations. Pour la production, il faudra Alembic.

## `get_session`

Le générateur ouvre une session SQLModel et la ferme automatiquement après la requête :

```python
with Session(engine) as session:
    yield session
```

FastAPI injecte cette session grâce à `Depends(get_session)`.

## Cycle de vie FastAPI

Le `lifespan` s’exécute au démarrage :

1. création du dossier audio ;
2. initialisation des tables ;
3. lancement de l’application.

## Middlewares

`SessionMiddleware` sert notamment à conserver l’état temporaire du parcours OAuth. En production, le cookie passe en HTTPS grâce à `https_only=True`.

`CORSMiddleware` autorise uniquement les origines configurées, les méthodes utiles et les en-têtes nécessaires.

## Endpoint `/api/health`

Il renvoie seulement `{"status": "ok"}`. Son rôle est de vérifier que le processus HTTP répond ; il ne garantit ni Mistral, ni SMTP, ni Google, ni la base distante.

## Limites à reconnaître

- SQLite convient au MVP local, pas à plusieurs conteneurs.
- `create_all` ne gère pas les changements de schéma.
- Le health check est superficiel.
- L’import final des routeurs dans `main.py` contient actuellement un défaut d’ordre détecté par Ruff. Les tests passent, mais `ruff check` retourne une erreur `I001`.

## Questions probables

**Pourquoi SQLModel ?**  
Il combine des modèles Pydantic et SQLAlchemy avec peu de code, ce qui convient au MVP.

**Pourquoi PostgreSQL plus tard ?**  
Pour la concurrence, les transactions, la persistance managée, les sauvegardes et plusieurs instances du backend.

**Pourquoi le backend affiche Not Found sur `/` ?**  
Parce qu’aucune route n’est définie à la racine. Le contrôle prévu est `/api/health` et la documentation est `/docs`.

---

# COMMIT 3 — Outils frontend React/Vite

[Voir le commit ed08945](https://github.com/AshDv/ScribeProject/commit/ed08945d27613f7d2942baf3e482465483e338bb)

## Objectif

Créer le point d’entrée frontend le plus simple possible et relier les appels `/api` au backend local.

## `index.html`

Il fournit :

- `lang="fr"` pour l’accessibilité et les lecteurs d’écran ;
- UTF-8 ;
- la largeur mobile ;
- une couleur de thème ;
- une description ;
- `<div id="root">`, point de montage React.

## `main.jsx`

`ReactDOM.createRoot(...).render(...)` monte `App` dans `#root`.

`React.StrictMode` active des contrôles supplémentaires en développement. Il peut exécuter certains effets deux fois en développement pour révéler les effets mal nettoyés ; ce comportement ne se produit pas ainsi dans le build de production.

## `package.json`

- `react` construit les composants.
- `react-dom` les affiche dans le navigateur.
- Vite lance le serveur et crée le build.
- Le plugin React traduit le JSX.
- `"type": "module"` active les imports ES modernes.

Commandes :

- `npm run dev` : développement ;
- `npm run build` : build optimisé ;
- `npm run preview` : lecture locale du build.

## `package-lock.json`

Il est généré par npm. Il contient les versions exactes et les sommes d’intégrité de toutes les dépendances indirectes.

Réponse orale :

> `package.json` exprime nos dépendances directes, tandis que `package-lock.json` garantit l’installation exacte et vérifiable de tout l’arbre.

## Proxy Vite

Le navigateur appelle `/api/...` sur le port 5174. Vite transmet ces demandes à `http://localhost:8000`.

Avantages :

- le frontend garde des URL relatives ;
- aucun changement dans chaque appel API ;
- le navigateur ne subit pas de différence d’origine pendant le développement.

`strictPort: true` empêche Vite de choisir silencieusement un autre port, ce qui casserait CORS et OAuth.

## Limites à reconnaître

- Vite 7.3.6 exige Node 20.19+ ou 22.12+, exigence qui n’était pas documentée dans la PR #3.
- Le proxy Vite ne sert qu’en développement. En production, un reverse proxy doit envoyer `/api` vers FastAPI ou le frontend doit utiliser une URL d’API configurée.
- Aucun routeur React n’est utilisé ; l’application choisit ses écrans avec une logique légère. C’est simple pour le MVP mais moins extensible.

---

# COMMIT 4 — Coquille et design de l’application

[Voir le commit 6104ac5](https://github.com/AshDv/ScribeProject/commit/6104ac55c5dad4fe4b6d7382a7ea5d17c9862250)

## Objectif

Créer la première page visible et un système de classes réutilisable pour les écrans suivants.

Le composant `App` de ce commit était volontairement une page temporaire. L’authentification, la navigation et les écrans finaux ont ensuite été ajoutés par d’autres commits.

## Principes CSS

- Variables globales pour les couleurs : `--ink`, `--muted`, `--green`, `--danger`.
- Classes réutilisables : boutons, cartes, alertes, statuts et champs.
- Grilles pour la page, les résultats et les formulaires.
- Breakpoints à 900 px et 560 px.
- Animations simples pour l’entrée, le micro et le chargement.
- Styles communs pour éviter de recopier les mêmes propriétés.

## Responsive

À moins de 900 px :

- la barre latérale devient une barre horizontale ;
- les grilles passent sur une colonne ;
- les zones d’authentification s’empilent.

À moins de 560 px :

- les marges diminuent ;
- les formulaires participants se réorganisent ;
- certains éléments secondaires disparaissent.

## Limites à reconnaître

- La feuille CSS est compacte mais dense. La séparation par composants ou modules CSS améliorerait la maintenance.
- Les polices Google sont chargées depuis un domaine externe. Pour une production RGPD stricte, il vaut mieux les auto-héberger.
- Le commit prépare des styles de fonctionnalités qui n’existaient pas encore dans le composant temporaire. C’est cohérent avec une base visuelle, mais le périmètre du commit est plus large que son petit `App.jsx`.
- Il faut encore auditer précisément le contraste, le clavier et les lecteurs d’écran.

---

# COMMIT 5 — Accord, retrait et effacement

[Voir le commit 4e21df6](https://github.com/AshDv/ScribeProject/commit/4e21df68d3c0241f1ca5d9b9751e8aeaf5315daa)

## Objectif

Faire respecter le consentement par le serveur, pas seulement par un bouton désactivé dans l’interface.

## Fonctions utilitaires

### `token_hash`

Le lien contient un jeton aléatoire. La base ne stocke que son empreinte SHA-256.

Quand un lien arrive, le backend recalcule l’empreinte et cherche la ligne correspondante. Une fuite de base ne révèle donc pas directement les liens utilisables.

### `owned_session`

Cette fonction vérifie que la réunion appartient à l’utilisateur connecté. Elle renvoie `404` pour ne pas confirmer l’existence d’une ressource appartenant à quelqu’un d’autre.

### `participants_for`

Elle centralise la lecture de tous les consentements d’une réunion.

### `is_active`

Un accord est actif seulement si :

- `consented_at` existe ;
- `withdrawn_at` est vide.

### `refresh_status`

La réunion devient `READY` uniquement si elle contient des participants et si tous les accords sont actifs. Sinon elle reste `PENDING`.

## Démarrage

`POST /api/consent-sessions/{id}/start` vérifie :

1. l’utilisateur est propriétaire ;
2. l’annonce en présentiel est confirmée ;
3. la liste des participants n’est pas vide ;
4. chaque consentement est actif.

Ensuite seulement, la réunion passe à `RECORDING` et les dates sont enregistrées.

## Retrait

`POST /api/public/consents/{token}/withdraw` :

1. enregistre la date du retrait ;
2. passe la réunion à `STOPPED` ;
3. enregistre la date d’arrêt.

Le backend devient immédiatement non autorisé à recevoir un nouvel audio pour cette réunion.

## Effacement

`DELETE /api/public/consents/{token}/data` :

- supprime les fichiers audio encore présents ;
- supprime les rapports structurés ;
- supprime les enregistrements liés ;
- anonymise le nom et l’e-mail du consentement ;
- remplace l’empreinte du jeton pour invalider l’ancien lien ;
- conserve une date de demande d’effacement.

`Path.resolve()` puis `is_relative_to(audio_directory)` empêchent de supprimer un fichier en dehors du dossier prévu.

## Codes HTTP

- `400` : demande incorrecte, par exemple annonce absente ;
- `404` : ressource ou lien introuvable ;
- `409` : état incompatible, par exemple accord manquant ;
- `204` : effacement réussi sans corps de réponse.

## Limites importantes

- Le retrait est stocké comme dernier état, pas comme un historique complet de tous les changements.
- Une personne peut accepter de nouveau avec le même lien après un retrait.
- Le détenteur du lien peut agir ; le lien est donc un secret de type bearer token.
- L’effacement d’un participant supprime actuellement le compte rendu complet de la réunion, donc aussi des données utiles aux autres participants. Une politique juridique plus fine devra arbitrer suppression, anonymisation et obligations de conservation.
- Aucun rate limiting n’est appliqué aux routes publiques.

## Question piège

**Le bouton frontend suffit-il à bloquer l’enregistrement ?**  
Non. Un utilisateur pourrait appeler l’API manuellement. Le serveur revérifie la propriété, l’état de la réunion et tous les consentements.

---

# COMMIT 6 — Page publique de consentement

[Voir le commit ecd894c](https://github.com/AshDv/ScribeProject/commit/ecd894ce955b396193fcc1300278517fbd4c3d35)

## Objectif

Permettre à un invité non connecté de comprendre le traitement, accepter, refuser, retirer son accord ou demander l’effacement.

## État React

- `notice` contient les informations du backend.
- `message` contient le résultat d’une action réussie.
- `error` contient une erreur lisible.

`useEffect` recharge les informations lorsque le jeton change.

## Fonction `act`

Elle reçoit une fonction API, l’exécute avec le jeton, affiche le résultat puis recharge l’état. Cela évite de dupliquer la même structure pour l’acceptation et le retrait.

## Affichage conditionnel

`active` vaut vrai si `consented_at` existe et `withdrawn_at` est vide.

Le bouton présenté dépend donc de l’état réel renvoyé par le serveur :

- accepter ;
- refuser ;
- retirer ;
- effacer.

## `PublicShell`

Le composant partage le même cadre visuel entre la page de consentement et la page d’information juridique. C’est une application du principe DRY.

## Évolution de `LegalGate`

Le commit sépare :

- l’acceptation des CGU ;
- la confirmation de lecture de l’information RGPD.

Le bouton reste bloqué tant que les deux cases ne sont pas cochées.

## Limites

- L’effacement ne possède pas de `try/catch` dans son gestionnaire inline.
- Après effacement, l’ancienne information reste à l’écran jusqu’au rechargement, même si le jeton est invalidé en base.
- `confirm()` est simple mais peu personnalisable.
- Il n’existe pas d’annulation de requête si le composant est démonté.
- En local, le lien `localhost` ne fonctionne que sur le PC qui héberge la base. Ce n’est pas un problème de jeton ; `localhost` désigne chaque machine elle-même.

---

# COMMIT 7 — Téléversement audio sécurisé

[Voir le commit 2a1dbd0](https://github.com/AshDv/ScribeProject/commit/2a1dbd0cc227d07739776329f5f517473913f15c)

## Objectif

Ne recevoir l’audio qu’après authentification et validation complète du consentement.

## `owned_recording`

La fonction vérifie que l’enregistrement appartient à l’utilisateur connecté. Elle est réutilisée pour la lecture et la suppression.

## `recording_detail`

Elle construit la réponse API :

- statut ;
- dates ;
- erreur éventuelle ;
- transcription ;
- segments ;
- résumé ;
- sujets ;
- décisions ;
- actions ;
- rapport détaillé s’il existe.

Les champs JSON stockés en texte sont reconvertis en listes avec `parse_json`.

## Création d’un enregistrement

`POST /api/recordings` reçoit du `multipart/form-data` :

- titre ;
- indicateur de consentement ;
- identifiant de réunion ;
- fichier audio.

Vérifications, dans l’ordre :

1. consentement déclaré ;
2. réunion existante et appartenant à l’utilisateur ;
3. réunion en état `RECORDING` ;
4. tous les participants encore consentants ;
5. type MIME autorisé ;
6. fichier non vide ;
7. taille inférieure à la limite.

Le serveur ne fait donc pas confiance au booléen envoyé par le navigateur.

## Formats

La table `ALLOWED_AUDIO` associe un type MIME à une extension sûre. Le nom original n’est pas conservé ; le serveur construit un nom avec l’UUID de l’enregistrement.

## Limite de taille

Le serveur lit `maximum + 1 octet`. Si ce dernier octet existe, le fichier dépasse la limite et reçoit `413`.

## Stockage et traitement

1. création de la ligne `Recording` ;
2. écriture du fichier temporaire ;
3. liaison à la session de consentement ;
4. commit SQL ;
5. ajout de `process_recording` aux tâches FastAPI ;
6. réponse `202 Accepted`.

`202` signifie que le fichier a été accepté mais que la transcription n’est pas encore terminée.

## Lecture et suppression

Les listes sont filtrées par `owner_id`. La suppression efface le lien, le rapport, le fichier et la ligne d’enregistrement.

## Limites importantes

- Le type MIME provient du client et ne garantit pas le vrai contenu binaire.
- Le fichier entier est chargé en mémoire, jusqu’à environ 50 Mo.
- `path.write_bytes` est synchrone dans une route `async`.
- Une erreur SQL après l’écriture pourrait laisser un fichier orphelin.
- `BackgroundTasks` travaille dans le même processus. Un redémarrage peut perdre le travail.
- Ce traitement n’est donc pas encore fiable dans un conteneur serverless qui peut disparaître après la réponse.

## Questions probables

**Pourquoi `202` et non `200` ?**  
Parce que la réponse confirme l’acceptation de l’audio, pas la fin du traitement.

**Comment empêchez-vous l’accès aux réunions des autres ?**  
Chaque lecture recherche la ressource puis compare `owner_id` à l’utilisateur extrait du JWT.

**Pourquoi ne pas garder le nom d’origine ?**  
Il peut contenir des données personnelles ou des caractères dangereux. L’UUID évite aussi les collisions.

---

# COMMIT 8 — Dictaphone du navigateur

[Voir le commit 1ae2765](https://github.com/AshDv/ScribeProject/commit/1ae2765b1bb0b9d585757c781a44ff2f4fc5b428)

## Objectif

Construire le parcours complet : préparation, attente des accords, enregistrement, écoute et envoi.

## Machine à états

```text
idle
  -> recording
  -> paused
  -> recording
  -> ready
  -> uploading
```

- `idle` : aucun audio ;
- `recording` : microphone actif ;
- `paused` : MediaRecorder suspendu ;
- `ready` : Blob créé et écoutable ;
- `uploading` : envoi au backend.

## Pourquoi `useState`

Les données visibles dans l’interface utilisent `useState` :

- état ;
- durée ;
- Blob ;
- URL d’écoute ;
- erreur.

Une modification provoque un nouveau rendu.

## Pourquoi `useRef`

Les objets techniques qui doivent survivre aux rendus sans déclencher un rendu utilisent `useRef` :

- instance `MediaRecorder` ;
- flux du microphone ;
- morceaux audio ;
- drapeau de retrait du consentement.

## Captation

`navigator.mediaDevices.getUserMedia({audio: true})` demande la permission microphone.

`MediaRecorder` produit des événements `dataavailable`. Chaque morceau non vide est ajouté dans `chunks.current`.

À l’arrêt :

1. création d’un `Blob` ;
2. création d’une URL locale avec `URL.createObjectURL` ;
3. passage à `ready` ;
4. arrêt des pistes du microphone.

## Nettoyage mémoire

Les URL Blob sont révoquées avec `URL.revokeObjectURL`. Les pistes audio sont arrêtées lors de l’arrêt et du démontage.

## Surveillance du consentement

Pendant `recording` ou `paused`, le frontend relit la réunion toutes les trois secondes.

Si la réunion n’est plus `recording` ou si un accord manque :

- le drapeau `consentRevoked` passe à vrai ;
- MediaRecorder s’arrête ;
- les morceaux sont supprimés ;
- aucune écoute n’est produite ;
- le microphone est coupé ;
- une erreur informe l’utilisateur.

Le drapeau est nécessaire parce que l’événement `onstop` s’exécute également lors d’un arrêt imposé.

## Préparation de réunion

`MeetingSetup` conserve une liste de participants dans un tableau. `update` produit un nouveau tableau au lieu de modifier directement l’état React.

`ConsentStatus` rafraîchit les accords toutes les trois secondes et désactive le bouton tant qu’ils ne sont pas tous actifs.

## Envoi

`createRecording` construit un `FormData`. Le helper générique ne force pas `Content-Type`, car le navigateur doit générer lui-même la frontière multipart.

## Limites importantes

- Un retrait est détecté avec un délai maximal d’environ trois secondes.
- Les erreurs du polling sont ignorées. En cas de perte réseau, le navigateur continue actuellement à enregistrer : une stratégie « fail closed » serait préférable.
- Des requêtes lentes peuvent se chevaucher toutes les trois secondes.
- `MediaRecorder` n’est pas identique dans tous les navigateurs.
- Le tableau utilise l’index comme clé React ; un identifiant temporaire serait plus robuste.
- Le bouton d’arrêt du dictaphone ne déclenche pas directement l’endpoint `stopConsentSession`.
- Après l’arrêt local, le backend revérifie néanmoins les consentements au moment de l’envoi.

## Questions probables

**Pourquoi un Blob ?**  
Un Blob représente les octets audio dans le navigateur sans avoir besoin d’un fichier permanent.

**Pourquoi une object URL ?**  
Elle permet au lecteur `<audio>` de lire le Blob localement sans l’envoyer.

**Pourquoi arrêter les pistes ?**  
Pour libérer le microphone et éteindre l’indicateur d’enregistrement du navigateur.

**Le retrait est-il instantané ?**  
Le backend change immédiatement l’état. Le navigateur le détecte au prochain contrôle, donc au maximum environ trois secondes si le réseau fonctionne.

---

# COMMIT 9 — Compte rendu structuré Mistral

[Voir le commit 1f88e83](https://github.com/AshDv/ScribeProject/commit/1f88e83fc774214614d25ddcfb07ea9ae989a4f1)

## Objectif

Obtenir un objet vérifiable plutôt qu’un simple texte libre.

## Modèles Pydantic

Le résultat attendu est découpé en types :

- `Speaker` : identifiant Voxtral, nom éventuel et niveau de certitude ;
- `KeyPoint` : sujet, détail, intervenants et sources ;
- `Decision` : décision, personnes, justification et sources ;
- `ActionItem` : tâche, responsable, échéance, priorité et sources ;
- `OpenQuestion` : question ouverte et responsable éventuel ;
- `Risk` : risque, réduction possible et responsable ;
- `Coverage` : classement de chaque segment ;
- `MeetingSummary` : objet final.

`Literal` limite certaines valeurs. `Field` limite notamment la longueur des actions et du résumé.

## Prompt système

Les règles principales sont :

- ne rien inventer ;
- préserver les dates, chiffres, objections et incertitudes ;
- lier chaque information aux `segment_ids` ;
- classer chaque segment exactement une fois ;
- n’attribuer une action que si elle est explicite ;
- laisser le responsable ou l’échéance à `null` si l’information manque ;
- associer un nom seulement après une identification explicite ;
- ne pas exposer les e-mails ;
- répondre dans la langue dominante.

## Données envoyées

Le payload contient :

- les noms des participants ;
- la transcription complète ;
- les segments avec temps, texte et intervenant.

Les e-mails ne sont pas envoyés au modèle.

## Paramètres

- modèle lu dans la configuration ;
- `temperature: 0` pour réduire la variation ;
- `top_p: 1` ;
- `safe_prompt: true` ;
- format de sortie JSON Schema strict ;
- timeout de 240 secondes.

Une température à zéro ne garantit pas l’absence d’hallucination. La qualité vient de la combinaison du prompt, du schéma, de Pydantic et du contrôle de couverture.

## Validation en quatre niveaux

1. Contrôle du code HTTP.
2. Lecture de `choices[0].message.content`.
3. Validation JSON avec `MeetingSummary.model_validate_json`.
4. Comparaison de tous les identifiants de segments avec `coverage`.

Le test :

```python
set(covered) == expected and len(covered) == len(expected)
```

vérifie qu’aucun segment ne manque et qu’aucun segment n’est dupliqué.

## Ce que « chaque mot a sa place » signifie réellement

Chaque segment est envoyé au modèle et doit apparaître une fois dans `coverage`. Cela ne signifie pas que chaque mot est répété dans le résumé. Les mots inutiles peuvent être classés comme `filler`, mais leur traitement reste traçable.

## Limites importantes

- Pas de retry avec backoff en cas de `429` ou `5xx`.
- Pas de limite liée au nombre de tokens ou à la longueur de réunion.
- Le texte et les segments envoient une partie de l’information deux fois, ce qui augmente le coût.
- `due_date` reste une chaîne non validée comme vraie date.
- Le contenu d’une réunion peut contenir une tentative de prompt injection. Le rôle système et le schéma réduisent le risque sans le supprimer.
- Une réponse sans `choices[0]` peut provoquer un `IndexError` non transformé en `SummaryError`.
- La sortie structurée ne prouve pas la vérité ; elle prouve surtout que la forme et la traçabilité demandées ont été respectées.

## Questions probables

**Pourquoi Pydantic après JSON Schema ?**  
Le fournisseur tente de respecter le schéma, puis notre application vérifie indépendamment le résultat avant de l’accepter.

**Comment sont attribués les noms ?**  
Voxtral fournit des identifiants de locuteur. Mistral peut les relier à un nom seulement si la personne s’identifie explicitement.

**Pourquoi `ensure_ascii=False` ?**  
Pour conserver les accents lisibles dans le JSON stocké.

**Pourquoi conserver `segment_ids` ?**  
Pour remonter de chaque décision ou action vers le passage source.

---

# COMMIT 10 — Chaîne Voxtral vers Mistral

[Voir le commit 15511bd](https://github.com/AshDv/ScribeProject/commit/15511bdaf809f905b2a76ab273e9f2f2be256469)

## Objectif

Relier toutes les briques et garantir la suppression de l’audio après la tentative de traitement.

## Session indépendante

La tâche reçoit seulement `recording_id`. Elle ouvre une nouvelle session SQLModel, car la session HTTP d’origine est fermée après la réponse `202`.

## Cycle de statut

```text
UPLOADED -> PROCESSING -> COMPLETED
                         \-> FAILED
```

Le statut `PROCESSING` est enregistré immédiatement afin que le frontend puisse afficher l’avancement.

## Recherche du contexte

La tâche retrouve :

- l’enregistrement ;
- la liaison avec la réunion ;
- les participants ;
- leurs noms.

Les noms sont transmis à Voxtral comme vocabulaire de contexte puis à Mistral pour une association prudente.

## Enchaînement

```python
transcript = transcribe_audio(...)
result = generate_summary(...)
```

La transcription produit le texte et les segments. Le résumé consomme ces deux éléments.

## Persistance

La table `Recording` reçoit des champs rapides :

- transcription ;
- segments ;
- résumé court ;
- sujets ;
- décisions ;
- actions.

`StructuredReport` reçoit les informations détaillées :

- modèle ;
- langue ;
- compte rendu ;
- intervenants ;
- points clés ;
- décisions ;
- actions ;
- questions ;
- risques ;
- couverture.

Le stockage JSON dans des colonnes texte est un compromis MVP : simple à écrire et relire, mais moins facile à requêter qu’un modèle relationnel complet.

## Gestion des erreurs

Les erreurs attendues de Voxtral, Mistral et du système de fichiers passent le statut à `FAILED` et sont enregistrées.

## Bloc `finally`

Il s’exécute après succès ou erreur :

1. vérifie que le chemin appartient au dossier audio ;
2. supprime le fichier ;
3. vide `audio_path` ;
4. arrête la réunion ;
5. enregistre la date d’arrêt.

La priorité est la minimisation : un échec de résumé ne justifie pas de conserver automatiquement l’audio.

## Limites importantes

- Un crash brutal du processus empêche l’exécution de `finally`.
- Une exception non prévue, comme un `IndexError` du format Mistral, peut laisser le statut déjà enregistré à `PROCESSING`.
- Après suppression de l’audio, un échec ne peut pas être rejoué sans nouvel enregistrement.
- La fonction ne refuse que l’état `PROCESSING`; un appel manuel sur un élément déjà terminé pourrait tenter un second traitement.
- L’ajout d’un second `StructuredReport` peut violer l’unicité.
- Les tâches FastAPI ne remplacent pas une file durable.
- Les champs résumés de `Recording` dupliquent une partie du rapport détaillé ; il faut les synchroniser.

## Questions probables

**Pourquoi ouvrir une nouvelle session SQL ?**  
Parce que la requête HTTP est déjà terminée et sa session a été fermée.

**Pourquoi deux tables pour le résultat ?**  
`Recording` donne une vue courte et rapide. `StructuredReport` porte le document détaillé et traçable. Pour une version plus grande, on formaliserait cette séparation et sa synchronisation.

**L’audio est-il toujours supprimé ?**  
Il est supprimé dans `finally` après les erreurs gérées, mais aucun code ne peut garantir un `finally` après une coupure brutale du processus ou de la machine.

---

# 4. Parcours complets à maîtriser

## Parcours de consentement

1. L’organisateur crée une session avec les participants.
2. Le backend génère un jeton par participant.
3. La base stocke seulement SHA-256 du jeton.
4. L’e-mail contient le jeton en clair.
5. Le participant ouvre la page publique.
6. Le backend recalcule SHA-256 et retrouve le consentement.
7. L’acceptation enregistre `consented_at`.
8. La réunion devient prête quand tous les accords sont actifs.
9. L’organisateur confirme l’annonce dans la salle.
10. Le backend passe la réunion à `RECORDING`.
11. Un retrait enregistre `withdrawn_at` et passe la réunion à `STOPPED`.
12. Le navigateur détecte cet état et arrête MediaRecorder.

## Parcours audio

1. Le navigateur demande le microphone.
2. MediaRecorder produit des morceaux.
3. L’arrêt crée un Blob.
4. L’utilisateur écoute le Blob local.
5. `FormData` envoie le Blob.
6. FastAPI vérifie JWT, propriété, état, consentements, MIME et taille.
7. Le fichier reçoit un nom UUID.
8. La base reçoit `Recording` et `SessionRecording`.
9. FastAPI répond `202`.
10. La tâche traite le fichier.

## Parcours IA

1. Voxtral reçoit l’audio.
2. Voxtral renvoie texte, segments, temps et identifiants de locuteur.
3. Mistral reçoit la transcription, les segments et les noms.
4. Mistral produit le JSON demandé.
5. Pydantic valide les types.
6. Le code vérifie la couverture des segments.
7. Le résultat court et le rapport détaillé sont stockés.
8. Le fichier audio est supprimé.

# 5. Résultats de la revue technique

Commandes exécutées sur `develop` au commit `9040eef` :

```powershell
python -m pytest -q
npm run build
python -m ruff check app tests
```

Résultats :

- 6 tests backend réussis ;
- build Vite réussi, 30 modules transformés ;
- aucune vulnérabilité npm signalée lors de l’installation locale ;
- Ruff trouve une erreur `I001` d’ordre des imports dans `server/app/main.py` ;
- 10 avertissements viennent de `python-jose`, qui utilise encore `datetime.utcnow()` en interne.

Les tests couvrent :

- inscription, connexion et profil ;
- refus d’inscription sans validation juridique ;
- refus d’un audio sans consentement ;
- confidentialité et suppression des enregistrements ;
- blocage avant consentement et arrêt après retrait ;
- erreur propre lorsque Google n’est pas configuré.

Ils ne couvrent pas encore :

- le vrai appel Voxtral ;
- le vrai appel Mistral ;
- le navigateur et MediaRecorder ;
- l’envoi SMTP réel ;
- les coupures réseau ;
- le pipeline complet dans `develop`.

# 6. Les faiblesses que le professeur peut trouver

## Niveau important

1. SQLite et les fichiers locaux ne conviennent pas à plusieurs instances.
2. `BackgroundTasks` n’est pas une file de traitement durable.
3. La surveillance du retrait continue à enregistrer si le réseau tombe.
4. La purge de 30 jours existe dans le dépôt mais n’est pas appelée au démarrage dans la PR #16.
5. L’effacement public supprime le rapport complet de la réunion.
6. Une exception Mistral inattendue peut laisser un élément en `PROCESSING`.

## Niveau moyen

1. Le MIME est déclaré par le client.
2. Le fichier est chargé entièrement en mémoire.
3. Le `.env` dépend du dossier depuis lequel le serveur est lancé.
4. Le health check ne teste pas les services externes.
5. Les polices Google sont externes.
6. Le proxy Vite est uniquement local.
7. La feuille CSS est compacte mais difficile à maintenir.
8. Le frontend ignore les erreurs du polling de consentement.

## Bonne réponse générale

> C’est une limite connue du MVP, pas une garantie que nous essayons de cacher. Le sprint valide le parcours fonctionnel local. La mise en production demande PostgreSQL, un stockage temporaire partagé, une file durable, des secrets managés, des migrations, des contrôles de disponibilité et un hébergement HTTPS.

# 7. Questions courtes et réponses à savoir

**KISS est-il respecté ?**  
Oui dans l’architecture MVP : un frontend, une API, une base et deux appels IA. Certaines fonctions doivent maintenant être séparées pour passer à la production.

**DRY est-il respecté ?**  
Les réglages, sessions SQL, appels API, coquilles publiques et détails d’enregistrement sont centralisés. Il reste une duplication volontaire entre le résumé court et le rapport détaillé.

**Pourquoi FastAPI ?**  
Typage, validation Pydantic, documentation OpenAPI automatique et faible quantité de code.

**Pourquoi React ?**  
Pour gérer clairement les états successifs du consentement, du micro et du traitement.

**Pourquoi SQLite ?**  
Zéro service supplémentaire pour le MVP local. PostgreSQL est prévu pour la production.

**Pourquoi SHA-256 pour le lien ?**  
Le jeton possède déjà une forte entropie. Nous avons besoin d’une recherche déterministe, pas d’un mot de passe lent à vérifier.

**SHA-256 chiffre-t-il le jeton ?**  
Non. C’est une empreinte irréversible utilisée pour comparer.

**Pourquoi bcrypt pour les mots de passe mais SHA-256 pour les liens ?**  
Un mot de passe humain est faible et nécessite un hash lent avec sel. Un jeton aléatoire de 256 bits est déjà imprévisible.

**Le booléen de consentement du frontend est-il fiable ?**  
Non. Le serveur revérifie les consentements stockés.

**Que signifie CORS ?**  
Le navigateur limite les appels entre origines. Le backend autorise explicitement le frontend prévu.

**Que signifie JWT ?**  
Un jeton signé contient l’identifiant utilisateur et une expiration. Le serveur vérifie la signature avant chaque route protégée.

**Pourquoi ne pas stocker l’audio ?**  
Minimisation RGPD et réduction du risque. Le produit final porte sur le compte rendu, pas l’archive audio.

**Qu’est-ce que la diarisation ?**  
La séparation de la transcription en segments associés à différents identifiants de locuteurs.

**La diarisation reconnaît-elle automatiquement Yanis ?**  
Non. Elle produit un identifiant. Le nom n’est associé qu’après une auto-identification explicite.

**Mistral peut-il halluciner ?**  
Oui. Température zéro, prompt, JSON Schema, Pydantic et couverture réduisent le risque sans l’annuler.

**Pourquoi une couverture des segments ?**  
Pour pouvoir démontrer qu’aucun segment n’a été oublié silencieusement.

**Pourquoi un timeout aussi long ?**  
Une réunion demande plus de temps qu’une petite requête texte. Il évite cependant une attente infinie.

**Pourquoi les JSON sont-ils stockés en texte ?**  
Pour rester simple avec SQLite. PostgreSQL JSONB ou des tables normalisées seraient plus adaptés aux recherches avancées.

**Pourquoi le lien de consentement est invalide sur un autre PC en local ?**  
Le lien pointe vers `localhost` et la base SQLite existe sur la machine d’Aymen. Chaque `localhost` désigne sa propre machine.

**Est-ce 100 % RGPD ?**  
Non. Des mesures techniques sont présentes, mais la validation juridique, les DPA, l’hébergement, les durées effectives et le registre restent nécessaires.

**Est-ce déjà 100 % serverless ?**  
Non. L’état local avec SQLite, disque et BackgroundTasks doit être adapté.

# 8. Démonstration technique conseillée

Avant la présentation :

```powershell
git rev-parse --short HEAD
git status --short
```

Résultat attendu :

```text
9040eef
```

Puis montrer :

1. `/api/health` ;
2. la création de la réunion ;
3. le blocage sans accord ;
4. l’acceptation publique ;
5. le déblocage ;
6. MediaRecorder et l’autorisation microphone ;
7. la transcription ;
8. le rapport ;
9. la disparition du fichier audio ;
10. les liens entre actions et segments.

# 9. Pitch personnel de 45 secondes

> J’ai posé la configuration commune du backend, la connexion SQLModel, le cycle FastAPI et l’outillage React/Vite. J’ai ensuite développé le parcours de consentement révocable, avec blocage côté serveur, page publique, arrêt du dictaphone et effacement. Pour l’audio, j’ai réalisé le dictaphone navigateur, les contrôles d’upload et la chaîne de traitement qui appelle Voxtral puis Mistral. Enfin, j’ai imposé une sortie JSON validée par Pydantic et une couverture de chaque segment, avant de supprimer l’audio dans le bloc de nettoyage.

# 10. Ce qu’il ne faut jamais prétendre

- Ne pas dire que l’absence d’hallucination est garantie.
- Ne pas dire que le retrait est détecté à la milliseconde.
- Ne pas dire que la conformité RGPD est juridiquement acquise.
- Ne pas dire que SQLite est prête pour tous les clients.
- Ne pas dire que l’audio est garanti supprimé après un crash machine.
- Ne pas dire que tous les 1 857 ajouts du commit frontend ont été écrits à la main.
- Ne pas dire que le MVP est déjà une architecture serverless de production.
- Ne pas attribuer à Yanis les commits d’authentification, de modèles SQL ou de transcription Voxtral.

La meilleure posture consiste à expliquer le fonctionnement exact, puis à distinguer clairement le MVP validé de l’industrialisation restante.

---

# 11. Mode d’emploi de cette version maximale

Les sections précédentes expliquent les fonctionnalités. Les sections suivantes descendent au
niveau attendu si le professeur montre une ligne au hasard et demande :

```text
Qu’est-ce que c’est ?
Pourquoi ce nom ?
Pourquoi cette syntaxe ?
Qu’est-ce qui entre ?
Qu’est-ce qui sort ?
Pourquoi l’avoir fait ainsi ?
Que se passe-t-il si cela échoue ?
Quelle serait la version de production ?
```

Pour répondre à n’importe quelle ligne, utiliser toujours cette méthode en sept points :

1. **Nature** : variable, fonction, classe, import, condition, boucle ou appel.
2. **Type** : texte, entier, booléen, liste, dictionnaire, objet, `None` ou promesse.
3. **Entrée** : valeur reçue par la ligne.
4. **Opération** : transformation ou vérification effectuée.
5. **Sortie** : valeur produite ou effet de bord.
6. **Raison** : besoin métier ou technique couvert.
7. **Limite** : erreur possible et amélioration de production.

Exemple avec :

```python
names = [item.name for item in participants if item.name]
```

Réponse complète :

> `names` est une variable locale. Sa valeur est une liste de chaînes. La compréhension parcourt
> les objets `participants`, garde seulement ceux dont le nom n’est pas vide et extrait leur
> attribut `name`. Cette liste sert de vocabulaire et de contexte aux modèles. La limite est qu’un
> nom peut être faux, effacé ou dupliqué ; en production, je normaliserais et dédupliquerais les
> valeurs.

# 12. Fondamentaux de programmation à maîtriser

## Programme, fichier et ligne

Un programme est un ensemble d’instructions exécutées par une machine. Le code source est le texte
lisible par les développeurs. Un fichier regroupe des instructions liées à une responsabilité.

Dans Scribe :

- `config.py` regroupe la configuration ;
- `db.py` regroupe l’accès à la base ;
- `routes.py` regroupe plusieurs routes HTTP ;
- `llm.py` décrit et appelle le modèle de résumé ;
- `processing.py` orchestre la transcription et le résumé ;
- `MeetingWorkflow.jsx` gère le parcours de réunion dans le navigateur.

Une ligne vide sépare visuellement les blocs. Un commentaire explique une intention. Une docstring,
placée entre triples guillemets en Python, documente un module, une classe ou une fonction.

## Variable

Une variable est un nom qui référence une valeur.

```python
path = Path(recording.audio_path).resolve()
```

- nom : `path` ;
- valeur : un objet `Path` ;
- portée : la fonction `process_recording` ;
- raison du nom : `path` désigne sans ambiguïté le chemin du fichier.

En JavaScript :

```javascript
const [seconds, setSeconds] = useState(0);
```

`seconds` est la valeur courante du compteur. `setSeconds` est la fonction fournie par React pour
demander une nouvelle valeur et un nouveau rendu.

Une variable n’est pas une boîte typée physiquement dans le code source. C’est un nom lié à une
valeur dans l’environnement d’exécution.

## Constante

Une constante est un nom qui ne doit pas être réaffecté.

En JavaScript, `const` interdit de réassigner le nom :

```javascript
const timer = setInterval(...);
```

Cela ne rend pas automatiquement le contenu d’un objet immuable.

En Python, les noms en majuscules expriment une convention de constante :

```python
SYSTEM_PROMPT = """..."""
```

Python n’empêche pas techniquement la réaffectation ; la majuscule communique l’intention.

## Types fondamentaux

| Type | Python | JavaScript | Exemple Scribe |
|---|---|---|---|
| Texte | `str` | `string` | titre, transcription |
| Entier | `int` | `number` | secondes, taille, ID de segment |
| Décimal | `float` | `number` | début et fin d’un segment |
| Booléen | `bool` | `boolean` | consentement actif |
| Absence | `None` | `null` / `undefined` | date ou responsable inconnu |
| Liste | `list` | `Array` | participants, segments |
| Dictionnaire | `dict` | objet simple | payload JSON |
| Objet métier | instance de classe | objet/composant | `Recording`, `MeetingSummary` |

### `None`, `null` et `undefined`

- `None` est l’absence de valeur en Python.
- `null` est une absence explicitement placée en JavaScript ou JSON.
- `undefined` signifie souvent qu’aucune valeur n’a été affectée ou renvoyée.

Le prompt impose `null` pour un responsable ou une échéance non explicitement prononcés, afin
d’éviter que le LLM invente.

## Dictionnaire

Un dictionnaire Python associe des clés à des valeurs :

```python
payload = {
    "participants": participant_names,
    "full_transcript": transcript,
    "diarized_segments": segments,
}
```

- les clés sont des chaînes ;
- les valeurs ont des types différents ;
- l’accès se fait par exemple avec `payload["participants"]`.

Le dictionnaire devient du JSON lorsqu’il est sérialisé. JSON ne connaît pas les classes Python :
il connaît objets, tableaux, chaînes, nombres, booléens et `null`.

## Liste

Une liste est une collection ordonnée :

```python
participants: list[ParticipantConsent]
```

L’ordre est conservé et l’index commence à zéro.

En JavaScript :

```javascript
const [participants, setParticipants] = useState([{ name: "", email: "" }]);
```

La valeur initiale est un tableau contenant un objet participant.

## Tuple

Un tuple Python est une séquence généralement utilisée comme structure fixe :

```python
deliveries: list[tuple[ParticipantInput, str]] = []
```

Chaque élément de `deliveries` contient exactement :

1. le participant ;
2. son token public en clair, gardé seulement en mémoire pour envoyer l’e-mail.

## Ensemble ou `set`

Un ensemble ne conserve qu’une occurrence de chaque valeur :

```python
if len(emails) != len(set(emails)):
```

Si la longueur diminue après conversion en ensemble, une adresse apparaît plusieurs fois.

Dans le contrôle de couverture :

```python
expected = {item["id"] for item in segments}
```

La compréhension entre accolades construit l’ensemble des identifiants attendus.

## Fonction

Une fonction est un bloc nommé et réutilisable. Elle peut recevoir des paramètres, produire une
valeur avec `return` et provoquer des effets de bord.

```python
def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()
```

- nom : `token_hash`, verbe implicite « calculer le hash du token » ;
- paramètre : `token` ;
- annotation d’entrée : `str` ;
- annotation de sortie : `str` ;
- corps : une instruction indentée ;
- résultat : une empreinte hexadécimale SHA-256.

Une fonction pure dépend seulement de ses entrées et ne modifie pas le monde extérieur.
`token_hash` est pratiquement pure. `process_recording` ne l’est pas : elle lit un fichier, appelle
des API, modifie la base et supprime l’audio.

## Paramètre et argument

Dans :

```python
def process_recording(recording_id: str) -> None:
```

`recording_id` est un paramètre.

Dans :

```python
process_recording(recording.id)
```

`recording.id` est l’argument donné à l’appel.

## Valeur de retour

`return result` renvoie l’objet au code appelant.  
`return` seul arrête la fonction sans valeur utile.  
Une annotation `-> None` annonce que la fonction ne renvoie rien d’utilisable.

## Classe

Une classe décrit la structure et le comportement d’un type d’objet.

```python
class ActionItem(BaseModel):
    task: str
    owner: str | None = None
```

`ActionItem` décrit une action de réunion. Elle hérite de `BaseModel`, donc Pydantic sait :

- valider les types ;
- créer un schéma JSON ;
- convertir l’instance en dictionnaire ;
- refuser certaines sorties invalides.

## Objet et instance

Une instance est un objet concret construit à partir d’une classe :

```python
StructuredReport(recording_id=recording.id, ...)
```

`StructuredReport` est la classe. Le résultat de l’appel est une instance représentant une ligne à
insérer.

Autre exemple :

```python
settings = get_settings()
```

`settings` est une instance de `Settings`.

## Constructeur

Le constructeur est le mécanisme qui initialise une nouvelle instance.

```python
Recording(
    owner_id=user.id,
    title=title.strip(),
)
```

SQLModel/Pydantic génère le constructeur à partir des champs annotés. Les arguments nommés rendent
la création lisible et évitent de dépendre de leur ordre.

En React fonctionnel, `Recorder` est un composant-fonction, pas une classe construite avec `new`.

## Module et import

Un module Python correspond généralement à un fichier `.py`.

```python
from app.llm import SummaryError, generate_summary
```

Cette ligne rend deux noms du module `app.llm` disponibles dans `processing.py`.

En JavaScript :

```javascript
import { useEffect, useRef, useState } from "react";
```

Il s’agit d’un import nommé depuis le paquet React.

## Condition

```python
if not consent:
    raise HTTPException(...)
```

La condition exécute le bloc si `consent` est faux.

```javascript
state === "idle" && <button ... />
```

En JSX, l’opérateur `&&` affiche le bouton seulement si la condition de gauche est vraie.

## Opérateur ternaire

Python :

```python
value_if_true if condition else value_if_false
```

JavaScript :

```javascript
condition ? valueIfTrue : valueIfFalse
```

Le composant utilise des ternaires imbriqués pour les libellés. C’est court, mais au-delà de deux
branches une fonction ou un objet de correspondance serait plus lisible.

## Boucle

```python
for link in links:
```

Le bloc est exécuté une fois par liaison.

En React :

```javascript
participants.map((participant) => <div ... />)
```

`map` transforme chaque participant en élément JSX et produit un nouveau tableau.

## Compréhension

```python
[item.topic for item in result.key_points]
```

Cette compréhension crée une liste de sujets en parcourant les points importants.

Elle est concise et lisible ici. Une compréhension avec trop de niveaux deviendrait contraire à
KISS.

## Exception

Une exception signale un traitement impossible :

```python
raise SummaryError("...")
```

`try` contient le code risqué, `except` traite certaines erreurs et `finally` s’exécute dans tous
les cas, succès ou échec.

```python
raise SummaryError(...) from exc
```

`from exc` conserve la cause technique dans la chaîne d’erreurs tout en présentant une erreur
métier.

## Gestionnaire de contexte

```python
with Session(engine) as session:
```

Le gestionnaire ouvre la session puis garantit sa fermeture à la sortie du bloc, même en cas
d’exception.

Autre exemple :

```python
with path.open("rb") as audio:
```

Le fichier est automatiquement fermé.

## Annotation de type Python

```python
def generate_summary(
    transcript: str,
    segments: list[dict],
    participant_names: list[str],
) -> MeetingSummary:
```

Les annotations documentent les types attendus. Python ne les applique pas automatiquement dans
toutes les fonctions. Pydantic les exploite dans ses modèles ; les IDE et outils statiques les
utilisent pour détecter des incohérences.

`str | None` signifie « chaîne ou absence ».  
`list[str]` signifie « liste de chaînes ».  
`Literal["low", "medium", "high"]` limite les valeurs autorisées.

## Synchrone et asynchrone

Une fonction Python normale est déclarée avec `def`. Une coroutine est déclarée avec `async def` et
peut attendre une opération non bloquante avec `await`.

En JavaScript, `async function` renvoie toujours une promesse. `await` suspend cette fonction
jusqu’au résultat sans bloquer toute l’interface.

Le code Mistral utilise `httpx.post` synchrone. Il est lancé comme tâche d’arrière-plan FastAPI, mais
ce n’est pas une file de tâches durable.

## Effet de bord

Un effet de bord est une modification extérieure à la valeur retournée :

- écrire un fichier ;
- modifier la base ;
- appeler Mistral ;
- afficher une interface ;
- écrire dans `localStorage` ;
- demander l’accès au microphone.

Identifier les effets de bord aide à savoir quoi tester et quoi nettoyer.

# 13. Python, PEP 8 et conventions du projet

## Python utilisé

Le projet cible Python 3.12 dans Ruff :

```toml
target-version = "py312"
```

Dans `3.12.x` :

- `3` est la version majeure ;
- `12` est la version mineure ;
- `x` est la version corrective.

Dire « le deuxième chiffre est toujours une mise à jour majeure » serait faux. Python 4 serait une
nouvelle version majeure.

## PEP 8

PEP 8 est le guide de style de Python. Il recommande notamment :

- quatre espaces par niveau d’indentation ;
- `snake_case` pour fonctions et variables ;
- `PascalCase` pour classes ;
- `UPPER_SNAKE_CASE` pour constantes ;
- imports organisés ;
- espaces autour des opérateurs ;
- lignes raisonnablement courtes ;
- deux lignes vides autour des définitions de haut niveau.

Exemples :

- `process_recording` : fonction en `snake_case` ;
- `recording_id` : variable en `snake_case` ;
- `MeetingSummary` : classe en `PascalCase` ;
- `SYSTEM_PROMPT` : constante en `UPPER_SNAKE_CASE`.

Le projet fixe 100 caractères par ligne, alors que la recommandation historique PEP 8 est plus
courte. C’est un choix d’équipe documenté dans `pyproject.toml`.

## Ruff

Ruff est un linter et formateur très rapide écrit en Rust. Les familles activées sont :

- `E` : erreurs de style Pycodestyle ;
- `F` : erreurs logiques Pyflakes, comme un import inutilisé ;
- `I` : ordre des imports ;
- `UP` : modernisation syntaxique ;
- `B` : pièges fréquents détectés par flake8-bugbear ;
- `SIM` : simplifications.

`B008` est ignorée, car FastAPI utilise volontairement :

```python
db: Session = Depends(get_session)
```

Un outil généraliste peut considérer un appel en valeur par défaut comme risqué. FastAPI l’interprète
comme une déclaration d’injection, pas comme une session créée à l’import.

## Nommage Python précis

| Nom | Pourquoi |
|---|---|
| `settings` | instance unique regroupant les réglages |
| `engine` | terme SQLAlchemy pour le point d’accès à la base |
| `session` / `db` | unité de travail ORM |
| `recording` | objet métier d’un enregistrement |
| `recording_id` | identifiant, et non l’objet complet |
| `meeting` | session de consentement liée à une réunion |
| `participants` | collection, donc pluriel |
| `names` | liste ne contenant plus que les noms |
| `path` | chemin de fichier sous forme de `Path` |
| `link` | ligne de liaison entre réunion et enregistrement |
| `result` | sortie structurée du résumé |
| `exc` | exception capturée |

# 14. JavaScript, JSX, React et TypeScript

## JavaScript

JavaScript est le langage exécuté par le navigateur. Le projet utilise JavaScript moderne avec des
modules ECMAScript.

## JavaScript vanilla

« Vanilla JavaScript » signifie JavaScript sans bibliothèque ou framework.

Scribe n’est pas une application entièrement vanilla, car l’interface utilise React. En revanche,
elle utilise directement plusieurs API natives du navigateur :

- `fetch` ;
- `navigator.mediaDevices.getUserMedia` ;
- `MediaRecorder` ;
- `Blob` ;
- `URL.createObjectURL` ;
- `setInterval` ;
- `localStorage`.

## JSX

JSX est une syntaxe qui permet d’écrire une structure proche du HTML dans JavaScript :

```jsx
<button onClick={start}>Démarrer</button>
```

Le navigateur ne comprend pas directement tous les JSX de développement. Vite et le plugin React
le transforment en appels JavaScript.

Différences avec HTML :

- `className` remplace `class` ;
- les expressions JavaScript sont entre accolades ;
- les événements utilisent `onClick`, `onChange` ;
- les composants commencent par une majuscule ;
- les balises doivent être correctement fermées.

## React

React est une bibliothèque d’interface utilisateur, pas un langage.

Le projet l’utilise pour :

- découper l’écran en composants ;
- stocker l’état ;
- recalculer l’affichage lorsque l’état change ;
- exécuter et nettoyer les effets ;
- réutiliser des composants.

Un framework impose généralement davantage de structure globale : routage, rendu serveur,
conventions de dossiers, accès aux données. React seul reste centré sur la vue.

## Composant

```javascript
function Recorder({ meeting, onCreated }) {
```

`Recorder` est un composant fonctionnel. Il reçoit des props et renvoie du JSX.

- `meeting` est un objet ;
- `onCreated` est une fonction fournie par le parent ;
- les accolades effectuent une déstructuration de l’objet de props.

## Prop

Une prop est une valeur transmise du parent à l’enfant. Elle doit être considérée comme en lecture
seule.

```jsx
<Recorder meeting={meeting} onCreated={onCreated} />
```

## État

L’état est une donnée interne dont le changement doit mettre à jour l’affichage.

```javascript
const [state, setState] = useState("idle");
```

Il ne faut pas faire directement :

```javascript
state = "recording";
```

React ne serait pas correctement informé. `setState("recording")` planifie le nouveau rendu.

## `useRef`

Une ref conserve une valeur entre les rendus sans provoquer de nouveau rendu quand `.current`
change.

Elle convient pour :

- l’objet `MediaRecorder` ;
- le flux microphone ;
- les morceaux audio ;
- le drapeau de retrait.

La seconde partie du nom indique la nature :

- `recorder` : objet MediaRecorder ;
- `stream` : MediaStream ;
- `chunks` : morceaux de Blob ;
- `consentRevoked` : booléen.

## `useEffect`

Un effet synchronise React avec un système extérieur :

- minuterie ;
- appel réseau répété ;
- microphone ;
- URL temporaire.

La fonction retournée par l’effet est le nettoyage :

```javascript
return () => clearInterval(timer);
```

Le tableau de dépendances dit quand recréer l’effet.

## TypeScript

TypeScript est un sur-ensemble de JavaScript ajoutant des annotations de types vérifiées avant
l’exécution.

Exemple TypeScript théorique :

```typescript
function formatTime(seconds: number): string
```

Le projet n’utilise pas TypeScript. Les fichiers sont `.js` et `.jsx`, pas `.ts` ou `.tsx`.

Avantages de TypeScript :

- erreurs de types détectées avant le navigateur ;
- meilleur autocomplètement ;
- contrats explicites entre API et composants ;
- refactorisation plus sûre.

Coût :

- configuration et compilation supplémentaires ;
- types à maintenir ;
- complexité supplémentaire pour un MVP très court.

Réponse honnête :

> Nous avons choisi JavaScript/JSX pour livrer rapidement un MVP KISS. Pour une équipe et une base
> qui grandissent, je passerais les contrats métier en TypeScript.

## Syntaxes JavaScript utilisées

### Fonction fléchée

```javascript
const formatTime = (seconds) => ...
```

Une fonction fléchée est une expression de fonction compacte.

### Déstructuration

```javascript
const [state, setState] = useState("idle");
```

La première valeur du tableau devient `state`, la seconde `setState`.

### Spread

```javascript
[...participants, { name: "", email: "" }]
```

`...participants` copie les références des éléments dans un nouveau tableau, puis ajoute le nouvel
objet. Cela évite de muter directement l’état React.

### Propriété calculée

```javascript
{ ...item, [field]: value }
```

Le nom de la propriété vient de la variable `field`. Cela permet à une fonction `update` de modifier
soit `name`, soit `email`.

### Chaîne modèle

```javascript
`E-mail du participant ${index + 1}`
```

Les accents graves créent une template literal et `${...}` insère une expression.

### Chaînage optionnel

```javascript
recorder.current?.stop()
```

La méthode n’est appelée que si la partie gauche n’est ni `null` ni `undefined`.

### Nullish et `||`

```javascript
recorder.current.mimeType || "audio/webm"
```

Si `mimeType` est une valeur falsy, le code utilise le format par défaut.

### Égalité stricte

```javascript
state === "recording"
```

`===` compare valeur et type sans conversion implicite. Il est préférable à `==`.

### Promesse

`fetch` renvoie une promesse, représentation d’un résultat futur. `await` récupère son résultat
dans une fonction `async`.

# 15. HTML, CSS et accessibilité

## HTML

HTML décrit la structure sémantique :

- `<main>` : contenu principal ;
- `<section>` : partie thématique ;
- `<header>` : en-tête ;
- `<h1>` : titre principal ;
- `<p>` : paragraphe ;
- `<form>` : formulaire ;
- `<label>` : libellé ;
- `<button>` : action ;
- `<audio>` : lecteur audio.

La sémantique aide :

- les lecteurs d’écran ;
- le clavier ;
- les moteurs ;
- la maintenance.

## CSS

CSS définit la présentation. Une règle contient :

```css
.record-button {
  background: var(--green);
  color: #fff;
}
```

- `.record-button` est le sélecteur de classe ;
- `background` et `color` sont les propriétés ;
- les valeurs déterminent le rendu.

## Cascade

CSS signifie Cascading Style Sheets. Plusieurs règles peuvent viser le même élément. Le navigateur
choisit selon :

- l’importance ;
- la spécificité ;
- l’ordre ;
- l’héritage.

## Variables CSS

```css
:root { --green: #167d64; }
```

`--green` centralise une couleur. `var(--green)` la réutilise. Cela applique DRY et facilite un
changement global.

## Flexbox et Grid

Flexbox gère principalement une dimension :

```css
display: flex;
align-items: center;
gap: 10px;
```

Grid organise des lignes et colonnes :

```css
display: grid;
grid-template-columns: 260px 1fr;
```

## Responsive

Les media queries changent les règles selon la largeur :

```css
@media (max-width: 900px) { ... }
```

À moins de 900 px, la barre latérale devient horizontale et les grilles passent sur une colonne.

## Accessibilité présente

- langue française dans `<html lang="fr">` ;
- vrais boutons pour les actions ;
- `aria-label` sur les champs dynamiques et boutons icônes ;
- labels sur plusieurs formulaires ;
- attribut `required` ;
- états `disabled` ;
- texte visible en plus des couleurs pour les statuts.

## Limites d’accessibilité

- aucune gestion explicite du focus après changement d’écran ;
- messages d’erreur sans `aria-live` ;
- contraste à vérifier avec un outil WCAG ;
- animations sans `prefers-reduced-motion` ;
- certains composants initiaux très compacts ;
- pas de tests lecteur d’écran ou navigation clavier documentés.

## Google Fonts et RGPD

Le CSS initial importe les polices depuis Google. Le navigateur contacte donc un domaine tiers, ce
qui peut transmettre notamment l’adresse IP.

Avant production, il serait préférable de :

- auto-héberger les fichiers de police ;
- ou utiliser les polices système ;
- documenter tout service tiers réellement conservé.

# 16. Stack technique exacte de la partie Yanis

## Frontend

| Élément | Rôle | Pourquoi |
|---|---|---|
| HTML5 | point d’entrée et sémantique | standard du Web |
| CSS | design et responsive | natif, sans dépendance UI lourde |
| JavaScript ES modules | logique navigateur | langage natif du navigateur |
| JSX | écriture des vues React | interface lisible et déclarative |
| React 18 | composants et état | bibliothèque légère et connue |
| ReactDOM | montage dans le DOM | pont entre React et la page |
| Vite | serveur et build | démarrage rapide, proxy simple |
| MediaDevices | autorisation microphone | API native |
| MediaRecorder | encodage audio navigateur | évite une bibliothèque audio |
| Fetch | appels HTTP | API native |

## Backend

| Élément | Rôle | Pourquoi |
|---|---|---|
| Python 3.12 cible | langage serveur | lisible, écosystème IA et API |
| FastAPI | routes HTTP | validation, OpenAPI, injection |
| Pydantic | validation des entrées/sorties | contrats typés |
| SQLModel | modèles et ORM | combine Pydantic et SQLAlchemy |
| SQLite | base locale | zéro serveur pour le MVP |
| httpx | appels Mistral | client HTTP Python |
| pathlib | chemins de fichiers | API sûre et lisible |
| BackgroundTasks | traitement après réponse | simple pour la démo |
| Uvicorn | serveur ASGI | exécute FastAPI |

## IA

| Élément | Rôle |
|---|---|
| Voxtral configuré | audio vers texte et diarisation |
| Mistral Medium 3.5 configuré | texte segmenté vers rapport structuré |
| JSON Schema | contrat demandé au LLM |
| Pydantic | validation réelle après génération |

## Développement

| Élément | Rôle |
|---|---|
| Git | historique distribué |
| GitHub | dépôt, branches et PR |
| npm | installation frontend |
| pip | installation Python |
| Ruff | lint Python |
| Pytest | tests |
| PowerShell | script local Windows |

# 17. API, REST, SDK et HTTP

## API

Une API est une interface permettant à deux logiciels de communiquer selon un contrat.

Exemples dans le projet :

- API HTTP de Scribe ;
- API Mistral ;
- API Web `MediaRecorder` du navigateur.

Le mot API ne désigne donc pas uniquement un site distant.

## SDK

Un SDK est un ensemble d’outils fourni pour développer avec une plateforme :

- bibliothèque cliente ;
- types ;
- helpers ;
- exemples ;
- parfois outils de test.

Dans `llm.py`, Yanis n’utilise pas un SDK Mistral. Il appelle directement l’API HTTP avec `httpx`.

Avantages :

- charge minimale ;
- payload entièrement visible ;
- peu d’abstraction.

Limites :

- il faut gérer soi-même le format, les erreurs et les évolutions ;
- moins de types fournis par le constructeur ;
- risque de décalage si le contrat change.

## REST

REST est un style d’architecture pour des ressources accessibles par HTTP.

Dans Scribe :

- `POST /api/recordings` crée un enregistrement ;
- `GET /api/recordings` liste ;
- `GET /api/recordings/{id}` lit ;
- `DELETE /api/recordings/{id}` supprime.

Le projet est REST-like. Il n’applique pas nécessairement tous les principes REST au sens académique,
notamment HATEOAS.

## Verbes HTTP

| Verbe | Sens |
|---|---|
| `GET` | lire sans modifier intentionnellement |
| `POST` | créer ou déclencher une action |
| `PUT` | remplacer une ressource |
| `PATCH` | modifier partiellement |
| `DELETE` | supprimer |

## Codes HTTP utilisés

| Code | Sens dans Scribe |
|---|---|
| 200 | lecture ou action réussie avec réponse |
| 201 | ressource créée |
| 202 | upload accepté, traitement lancé ensuite |
| 204 | suppression réussie sans corps |
| 400 | donnée métier refusée |
| 401 | authentification nécessaire |
| 404 | ressource absente ou cachée |
| 409 | conflit d’état, par exemple accord manquant |
| 413 | fichier trop volumineux |
| 415 | format média refusé |
| 422 | validation automatique impossible |
| 503 | service/configuration indisponible |

## JSON

JSON est un format texte d’échange. Il ressemble aux dictionnaires Python et objets JavaScript, mais
ce n’est ni l’un ni l’autre.

Exemple :

```json
{
  "status": "accepted",
  "consented_at": "2026-07-23T12:00:00Z"
}
```

## `multipart/form-data`

Un fichier audio ne passe pas dans le JSON du projet. `FormData` construit une requête multipart
contenant :

- titre ;
- booléen de consentement converti en texte ;
- ID de réunion ;
- fichier binaire.

## Autres types d’API

### GraphQL

Le client envoie une requête décrivant exactement les champs souhaités vers un endpoint principal.
C’est utile pour des graphes riches, mais plus complexe qu’une petite API REST.

### SOAP

Protocole XML très structuré avec contrats WSDL, fréquent dans des systèmes d’entreprise anciens ou
fortement normalisés.

### gRPC

Appels binaires basés sur Protocol Buffers, performants entre services, moins naturels directement
depuis un navigateur.

### WebSocket

Connexion bidirectionnelle persistante, utile pour du temps réel. Le MVP utilise un polling toutes
les trois secondes, plus simple mais moins instantané.

### Webhook

Appel HTTP envoyé par un service lorsqu’un événement survient. Une future architecture pourrait
recevoir un webhook de fin de transcription.

# 18. SQL, NoSQL, ORM et tables touchées

## Base de données

Une base de données conserve les informations au-delà de la mémoire d’un processus.

## SQL

Une base relationnelle organise les données en tables avec :

- colonnes ;
- lignes ;
- clés primaires ;
- clés étrangères ;
- contraintes ;
- requêtes SQL.

SQLite est relationnelle et utilise SQL.

## NoSQL

NoSQL regroupe plusieurs modèles non relationnels :

- documents, par exemple MongoDB ;
- clé-valeur, par exemple Redis ;
- colonnes larges ;
- graphes.

NoSQL ne signifie pas « aucune structure » ni « toujours plus rapide ».

## ORM

ORM signifie Object-Relational Mapping. Il relie les objets du langage aux lignes SQL.

```python
recording = session.get(Recording, recording_id)
```

Le développeur manipule un objet `Recording`. SQLModel/SQLAlchemy génère une requête SQL.

Avantages :

- cohérence avec les types Python ;
- moins de SQL répétitif ;
- requêtes composables ;
- protection naturelle contre l’injection quand les valeurs sont paramétrées.

Limites :

- peut masquer les requêtes réellement exécutées ;
- risque de requêtes nombreuses ;
- besoin de comprendre SQL pour optimiser ;
- certaines requêtes complexes sont plus claires en SQL.

## Tables utilisées par Yanis

Les classes des tables ont été créées principalement par Ashwin. Yanis les manipule ainsi :

### `ConsentSession`

Une réunion préparée :

- propriétaire ;
- titre ;
- état ;
- dates de démarrage et d’arrêt ;
- confirmation de l’annonce orale.

Yanis change son statut lors du démarrage, du retrait et de la fin du traitement.

### `ParticipantConsent`

Une invitation individuelle :

- nom ;
- e-mail ;
- hash du token ;
- version de notice ;
- date d’accord ;
- date de retrait ;
- demande d’effacement.

Yanis la lit, la met à jour et l’anonymise.

### `Recording`

Un enregistrement et ses résultats principaux :

- propriétaire ;
- métadonnées audio ;
- statut ;
- transcription ;
- segments ;
- résumé ;
- thèmes ;
- décisions ;
- actions.

Yanis insère la ligne, met à jour le traitement et peut la supprimer.

### `SessionRecording`

Table de liaison entre une réunion de consentement et un enregistrement.

Elle empêche de mettre directement toutes les informations dans une seule table et permet de
retrouver le contexte.

### `StructuredReport`

Rapport détaillé :

- modèle utilisé ;
- langue ;
- minutes détaillées ;
- locuteurs ;
- points clés ;
- décisions ;
- actions ;
- questions ;
- risques ;
- couverture.

Yanis construit et insère cette instance dans `processing.py`.

## `add`, `commit`, `refresh`, `delete`

```python
session.add(recording)
```

Place l’objet dans l’unité de travail.

```python
session.commit()
```

Valide la transaction dans la base.

```python
session.refresh(recording)
```

Recharge les valeurs produites ou confirmées par la base.

```python
session.delete(recording)
```

Marque la ligne pour suppression au prochain commit.

# 19. IA : STT, LLM, diarisation et structured output

## IA générative

Une IA générative produit du contenu à partir d’une entrée. Un LLM prédit des tokens selon le
contexte et ses paramètres.

## Token

Un token est une unité traitée par le modèle. Ce n’est pas toujours un mot : un mot peut être
découpé en plusieurs tokens, et la ponctuation peut compter.

Les coûts et limites des LLM sont souvent exprimés en tokens d’entrée et de sortie.

## STT

STT signifie Speech-to-Text : transformer un signal audio en texte.

Voxtral est appelé par la partie transcription écrite par Ashwin. Yanis reçoit sa sortie dans
`process_recording`.

## Diarisation

La diarisation répond à « qui parle quand ? » en séparant des segments par identifiants de locuteurs.

Elle ne connaît pas automatiquement l’identité civile. Elle peut produire `speaker_0`, `speaker_1`.
Le prompt n’associe un nom qu’en cas d’auto-identification ou de preuve non ambiguë.

## LLM

Le LLM reçoit :

- transcription complète ;
- segments diarisés ;
- noms des participants.

Il produit :

- résumé exécutif ;
- compte rendu détaillé ;
- locuteurs ;
- points clés ;
- décisions ;
- actions ;
- questions ouvertes ;
- risques ;
- couverture des segments.

## Pourquoi deux modèles

La tâche audio et la tâche de synthèse sont différentes :

- un modèle de transcription traite un signal sonore ;
- un modèle de langage structure et synthétise du texte.

Cette séparation permet de choisir et comparer chaque brique.

## Pourquoi Voxtral Mini configuré

Le choix vise le compromis du MVP :

- modèle destiné à l’audio ;
- coût et latence plus faibles qu’un très gros modèle ;
- diarisation demandée ;
- intégration avec la même plateforme Mistral.

Ce choix doit être confirmé par un benchmark réel sur :

- accents ;
- bruit ;
- réunions longues ;
- chevauchements ;
- vocabulaire métier ;
- coût ;
- latence.

## Pourquoi Mistral Medium 3.5 configuré

Le besoin n’est pas seulement de reformuler. Il faut :

- suivre de nombreuses règles ;
- produire une structure riche ;
- lier les éléments aux segments ;
- conserver les incertitudes ;
- éviter les attributions inventées.

Un modèle intermédiaire vise un meilleur raisonnement structuré qu’un petit modèle, avec un coût
inférieur à un modèle maximal.

Réponse prudente :

> `mistral-medium-3-5` est la valeur configurée dans le projet. Avant déploiement, je vérifie que cet
> identifiant est disponible pour le compte et je benchmarke qualité, latence et coût. Un nom dans
> le `.env` ne prouve pas à lui seul qu’un modèle est accessible.

## Prompt

Un prompt est l’ensemble des instructions et données envoyées au modèle.

Le message `system` fixe le rôle et les règles. Le message `user` contient les données de la réunion.
Séparer les deux rend l’intention plus claire.

## Hallucination

Une hallucination est une sortie plausible mais non soutenue par l’entrée.

Le projet réduit ce risque avec :

- température zéro ;
- interdiction explicite d’inventer ;
- `null` si une information manque ;
- liens vers les segments ;
- JSON Schema strict ;
- validation Pydantic ;
- contrôle de couverture.

Il ne le supprime pas.

## Température

`temperature: 0` réduit l’aléatoire et favorise la reproductibilité. Cela ne transforme pas le LLM
en système déterministe ou infaillible.

## `top_p`

`top_p: 1` ne restreint pas la masse de probabilité par nucleus sampling. Avec température zéro,
l’objectif reste une sortie peu créative.

## JSON Schema

Le JSON Schema décrit :

- champs ;
- types ;
- valeurs autorisées ;
- sous-objets ;
- tableaux.

Le modèle reçoit ce contrat via `response_format`.

## Validation Pydantic

Même si le fournisseur promet une sortie structurée, le serveur valide réellement :

```python
MeetingSummary.model_validate_json(content)
```

Un résultat invalide devient une erreur contrôlée et n’est pas enregistré comme rapport valide.

## Couverture

Chaque segment doit apparaître exactement une fois dans `coverage`.

Nuance essentielle :

> Le contrôle prouve une couverture au niveau des identifiants de segments. Il ne prouve pas que
> chaque mot est reproduit, compris correctement ou utilisé dans le résumé.

# 20. Git, commits, branches et noms

## Git

Git est un système de gestion de versions distribué. Chaque clone possède l’historique. Un commit
est un instantané identifié par un hash.

## GitHub

GitHub héberge le dépôt et ajoute :

- pull requests ;
- revue ;
- règles de branche ;
- issues ;
- intégrations.

## Branche

Une branche est un pointeur mobile vers une série de commits.

Le travail doit suivre :

```text
develop
  \-- branche de fonctionnalité
        \-- petits commits
              \-- pull request
                    \-- revue
                          \-- fusion dans develop
```

## Pull request

Une PR demande la fusion d’une branche. Elle permet :

- de lire le diff ;
- de discuter ;
- de lancer les contrôles ;
- de demander une approbation ;
- de garder la trace.

## Conventional Commits

Les messages suivent :

```text
type(scope): action
```

### Types utilisés

- `chore` : fondation, configuration ou outillage sans fonctionnalité utilisateur directe ;
- `feat` : nouvelle fonctionnalité.

### Scopes utilisés

- `api` : backend HTTP ;
- `web` : fondation frontend ;
- `consent` : logique serveur du consentement ;
- `consent-ui` : interface du consentement ;
- `recording` : stockage/upload audio ;
- `recorder` : dictaphone navigateur ;
- `summary` : production du rapport ;
- `processing` : orchestration.

### Pourquoi les verbes à l’impératif anglais

`add`, `generate`, `connect` décrivent ce que fait le commit si on l’applique.

## Explication des dix noms

| Commit | Décomposition |
|---|---|
| `chore(api): add backend configuration` | fondation backend, pas encore une feature utilisateur |
| `chore(api): add database and health endpoint` | moteur DB et endpoint de santé |
| `chore(web): add frontend tooling` | outils React/Vite |
| `chore(web): add application shell` | première structure et design |
| `feat(consent): add accept and withdrawal` | endpoints d’accord et retrait |
| `feat(consent-ui): add public consent page` | interface publique correspondante |
| `feat(recording): add secure audio upload` | contrôles serveur de l’upload |
| `feat(recorder): add browser dictaphone` | captation dans le navigateur |
| `feat(summary): generate structured meeting reports` | schéma, prompt et appel LLM |
| `feat(processing): connect transcription and summary` | orchestration de bout en bout |

## Limite de l’atomicité

Plusieurs commits sont fonctionnellement cohérents, mais pas minimaux au niveau d’une seule petite
modification :

- le CSS de la coquille contient déjà des classes de fonctionnalités futures ;
- le commit d’upload ajoute plusieurs endpoints ;
- le dictaphone ajoute aussi la préparation et le suivi des accords.

Réponse honnête :

> Les commits correspondent à des incréments démontrables, mais certains auraient pu être divisés
> davantage. Un commit atomique ne signifie pas « une ligne » ; il signifie une intention
> indépendante, testable et réversible.

## Commits de fusion

Yanis apparaît aussi comme auteur de certains merges GitHub. Ils prouvent une participation à
l’intégration, mais ne doivent pas être comptés comme du code fonctionnel personnel écrit par lui.

## Harness IA

Un « AI coding harness » est l’environnement qui permet à un agent de développement d’inspecter un
dépôt, modifier des fichiers, exécuter des commandes et vérifier le résultat.

Exemples génériques :

- Codex ;
- Claude Code ;
- autres agents intégrés à un terminal ou un IDE.

Le harness n’est pas le langage ni le produit final. Les preuves attendues restent :

- compréhension du code ;
- revue humaine ;
- tests ;
- décisions justifiées ;
- historique Git cohérent.

## Dockerfile

Un Dockerfile est une recette texte pour construire une image de conteneur :

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["uvicorn", "app.main:app"]
```

Le dépôt officiel étudié n’utilise pas de Dockerfile dans les dix commits de Yanis. Le lancement
local repose sur `start.ps1`.

Il ne faut donc pas prétendre avoir conteneurisé cette version.

## Le signe `$`

En PowerShell :

```powershell
$serverPath
```

`$` indique une variable.

En JavaScript, `$` n’est pas nécessaire pour une variable, mais `${...}` insère une expression dans
une template literal.

---

# 21. COMMIT 1 ligne par ligne — fondation backend

[Commit complet](https://github.com/AshDv/ScribeProject/commit/2646623fc7c4bf83106cc4629ffa934131303012)

## `.gitignore`

[Voir le fichier dans ce commit](https://github.com/AshDv/ScribeProject/blob/2646623fc7c4bf83106cc4629ffa934131303012/.gitignore)

Chaque motif dit à Git quels fichiers locaux ne doivent pas entrer dans l’historique.

| Ligne ou motif | Explication |
|---|---|
| `__pycache__/` | cache d’exécution Python, régénérable |
| `*.py[cod]` | bytecode `.pyc`, `.pyo`, `.pyd` |
| `.venv/`, `venv/` | environnements Python contenant des paquets locaux |
| `*.egg-info/` | métadonnées de paquet Python générées |
| `.env` | secrets et configuration locale |
| `.env.*` | variantes locales comme `.env.production` |
| `!.env.example` | exception : le modèle sans secret reste versionné |
| `*.db`, `*.sqlite3` | bases locales contenant des données |
| `server/data/` | fichiers audio temporaires |
| `node_modules/` | dépendances npm téléchargées |
| `dist/` | build frontend généré |
| `.vite/` | cache Vite |
| `.DS_Store`, `Thumbs.db` | métadonnées macOS et Windows |
| `.idea/`, `.vscode/` | réglages locaux d’IDE |
| `*.log` | journaux susceptibles de contenir des données |
| `tmp/`, `outputs/`, `test/` | artefacts locaux hors produit |
| `preproduction.pdf` | ancien document de travail |
| `team-delivery-kit/` | kit local d’intégration |

Pourquoi versionner `package-lock.json` mais pas `node_modules` :

- le lockfile décrit exactement les versions ;
- `node_modules` contient les copies volumineuses recréées par npm.

Limite : retirer un secret de `.gitignore` après l’avoir commité ne l’efface pas de l’historique.
Il faut révoquer le secret puis nettoyer l’historique si nécessaire.

## `pyproject.toml`

[Lignes 1 à 10](https://github.com/AshDv/ScribeProject/blob/2646623fc7c4bf83106cc4629ffa934131303012/pyproject.toml#L1-L10)

```toml
[tool.ruff]
line-length = 100
target-version = "py312"
```

- `[tool.ruff]` ouvre une section TOML destinée à Ruff.
- `line-length` fixe la largeur choisie par l’équipe.
- `target-version` autorise les règles et syntaxes compatibles Python 3.12.

```toml
[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM"]
ignore = ["B008"]
```

- `select` choisit les familles de contrôles.
- `ignore` désactive précisément une règle incompatible avec l’usage normal de `Depends`.
- le commentaire après `#` n’est pas exécuté.

```toml
[tool.pytest.ini_options]
testpaths = ["server/tests"]
```

Pytest cherchera par défaut les tests dans ce dossier.

TOML est un format de configuration, pas un langage de programmation général.

## `server/.env.example`

[Lignes 1 à 32](https://github.com/AshDv/ScribeProject/blob/2646623fc7c4bf83106cc4629ffa934131303012/server/.env.example#L1-L32)

Le vrai `.env` est une suite `NOM=valeur`. Les noms sont en `UPPER_SNAKE_CASE`, convention des
variables d’environnement.

| Variable | Utilité | Secret ? |
|---|---|---|
| `ENVIRONMENT` | active les différences développement/production | non |
| `SECRET_KEY` | signe les sessions et JWT | oui |
| `DATABASE_URL` | indique le moteur et l’emplacement de la base | parfois |
| `CORS_ORIGINS` | origines navigateur autorisées | non |
| `FRONTEND_URL` | adresse de retour vers React | non |
| `API_PUBLIC_URL` | adresse publique de FastAPI | non |
| `UPLOAD_DIR` | dossier temporaire audio | non |
| `MAX_AUDIO_MB` | taille maximale acceptée | non |
| `RESULT_RETENTION_DAYS` | durée annoncée des résultats | non |
| `DATA_CONTROLLER_NAME` | responsable juridique | donnée publique |
| `DATA_CONTROLLER_ADDRESS` | adresse juridique | donnée publique |
| `PRIVACY_CONTACT_EMAIL` | contact droits RGPD | donnée publique |
| `MISTRAL_API_KEY` | authentifie les appels IA et engage le quota | oui |
| `VOXTRAL_MODEL` | modèle STT demandé | non |
| `SUMMARY_MODEL` | modèle de compte rendu demandé | non |
| `GOOGLE_CLIENT_ID` | identifie l’application chez Google | plutôt public |
| `GOOGLE_CLIENT_SECRET` | prouve l’identité du backend à Google | oui |
| `SMTP_HOST` | serveur d’e-mail | non |
| `SMTP_PORT` | port du serveur | non |
| `SMTP_USERNAME` | compte SMTP | sensible |
| `SMTP_PASSWORD` | secret SMTP | oui |
| `SMTP_FROM_EMAIL` | expéditeur visible | non |
| `SMTP_USE_TLS` | demande le chiffrement de transport | non |

Le `.env.example` contient des emplacements vides et de fausses valeurs. Il constitue un contrat de
configuration.

Le vrai fichier se trouve dans `server/.env`, car le script démarre Uvicorn depuis `server` et
`SettingsConfigDict(env_file=".env")` cherche relativement au répertoire courant.

Pourquoi les commentaires commencent par `#` : ils documentent sans devenir des variables.

Pourquoi le port SMTP est `587` : c’est le port habituel de soumission avec STARTTLS. Cela ne
garantit pas que le fournisseur l’accepte.

Pourquoi `SMTP_USE_TLS=true` : Pydantic convertit le texte en booléen.

Pourquoi une seule clé Mistral : le même compte API authentifie l’endpoint audio et l’endpoint chat.
Les coûts et autorisations restent ceux du compte.

Erreur à ne jamais faire : placer les vraies clés dans `.env.example`.

## `server/app/__init__.py`

[Lignes 1 et 2](https://github.com/AshDv/ScribeProject/blob/2646623fc7c4bf83106cc4629ffa934131303012/server/app/__init__.py#L1-L2)

```python
"""Scribe — backend simple (FastAPI + Vexa + LLM)."""
__version__ = "1.0.0"
```

- `__init__.py` marque `app` comme paquet Python.
- la première ligne est la docstring du paquet.
- `__version__` est une variable spéciale conventionnelle de version.

Point de revue : la mention `Vexa` est un reste qui ne correspond plus à l’architecture du dictaphone
local étudiée. Elle devrait être retirée pour éviter une documentation mensongère.

## `server/app/config.py`

[Lignes 1 à 74](https://github.com/AshDv/ScribeProject/blob/2646623fc7c4bf83106cc4629ffa934131303012/server/app/config.py#L1-L74)

### Lignes 1 à 6 — documentation et imports

```python
"""Configuration centralisée de Scribe."""
from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
```

- la docstring annonce la responsabilité unique du module ;
- `lru_cache` mémorise le résultat d’une fonction ;
- `Path` représente un chemin de façon portable ;
- `BaseSettings` charge et valide l’environnement ;
- `SettingsConfigDict` configure ce chargement.

### Ligne 9 — classe

```python
class Settings(BaseSettings):
```

`Settings` est en PascalCase parce que c’est une classe. L’héritage apporte le constructeur, la
validation et la lecture des variables d’environnement.

### Ligne 10 — configuration Pydantic

```python
model_config = SettingsConfigDict(env_file=".env", extra="ignore")
```

- `env_file` indique le fichier de repli ;
- les variables système peuvent surcharger le fichier ;
- `extra="ignore"` n’échoue pas si une variable ancienne ou externe est présente.

Avantage : déploiement plus tolérant.  
Limite : une faute dans le nom d’une variable supplémentaire peut passer silencieusement.

### Lignes 12 à 27 — réglages applicatifs

Chaque ligne suit :

```python
nom: type = valeur_par_défaut
```

L’annotation permet la conversion.

- `app_name: str` : nom humain.
- `environment: str` : mode d’exécution.
- `secret_key: str` : valeur de développement à remplacer.
- `database_url: str` : URL SQLAlchemy ; `sqlite:///` indique un fichier local.
- `cors_origins: str` : chaîne pouvant contenir plusieurs origines séparées par virgules.
- `frontend_url` : destination du navigateur.
- `api_public_url` : origine publique du callback.
- `token_minutes: int = 60 * 24` : calcul lisible d’une journée, évalué au chargement.
- `upload_dir` : stockage temporaire.
- `max_audio_mb` : limite métier.
- `result_retention_days` : politique de conservation annoncée.
- `terms_version`, `privacy_version` : textes légaux acceptés.
- données du responsable : volontairement vides tant qu’elles ne sont pas configurées.

La valeur par défaut de `secret_key` est dangereuse en production. Le code ne force pas encore son
remplacement.

### Lignes 29 à 42 — services externes

```python
mistral_api_key: str | None = None
```

Le type union signifie que la clé peut manquer au démarrage. La fonctionnalité échouera ensuite avec
un message clair.

Même principe pour Google et SMTP : le backend peut démarrer sans ces services.

`smtp_port: int = 587` montre une conversion de texte d’environnement vers entier.

### Lignes 44 à 46 — `cors_list`

```python
@property
def cors_list(self) -> list[str]:
    return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]
```

- `@property` permet `settings.cors_list` sans parenthèses ;
- `self` est l’instance courante ;
- `split(",")` découpe ;
- `strip()` retire les espaces ;
- le `if` retire les éléments vides ;
- la sortie est une liste de chaînes.

### Lignes 48 à 50 — `audio_directory`

```python
return Path(self.upload_dir).resolve()
```

`resolve` construit un chemin absolu. Cela facilite les contrôles empêchant la suppression hors du
dossier.

Nuance : un chemin résolu n’assure pas à lui seul qu’il se trouve dans le dossier autorisé. C’est
pourquoi le code vérifie ensuite `is_relative_to`.

### Lignes 52 à 58 — services configurés

`bool(a and b)` transforme la présence des valeurs en vrai/faux.

- Google exige ID et secret.
- SMTP vérifie seulement hôte et expéditeur.

Cette vérification est minimale : elle ne teste ni réseau, ni identifiants.

### Lignes 60 à 66 — juridique configuré

La propriété exige :

- nom ;
- adresse ;
- contact différent du placeholder.

Elle ne constitue pas une validation juridique.

### Lignes 69 à 74 — singleton de configuration

```python
@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
```

`@lru_cache` sans parenthèses utilise les réglages par défaut. Comme la fonction n’a aucun argument,
elle conserve une seule instance.

Conséquences :

- pas de relecture à chaque requête ;
- même configuration partout ;
- redémarrage nécessaire après modification ;
- en test, il faut définir l’environnement avant l’import ou vider le cache.

## `server/app/processing.py` initial

[Lignes 1 à 5](https://github.com/AshDv/ScribeProject/blob/2646623fc7c4bf83106cc4629ffa934131303012/server/app/processing.py#L1-L5)

```python
def process_recording(_: str) -> None:
    raise RuntimeError("Le traitement audio n’est pas encore configuré")
```

- la fonction réserve le contrat futur ;
- `_` signifie « paramètre volontairement non utilisé » ;
- son type est `str` ;
- `-> None` annonce aucune sortie ;
- l’exception évite de prétendre que le traitement fonctionne.

Le commit 10 remplace ce placeholder sans changer le nom public, ce qui permet aux routes de
dépendre tôt d’une interface stable.

## `server/requirements.txt`

[Lignes 1 à 15](https://github.com/AshDv/ScribeProject/blob/2646623fc7c4bf83106cc4629ffa934131303012/server/requirements.txt#L1-L15)

`==` fixe exactement la version afin de rendre l’installation reproductible.

| Paquet | Rôle |
|---|---|
| `fastapi` | framework API |
| `uvicorn[standard]` | serveur ASGI avec dépendances standard |
| `sqlmodel` | ORM et modèles |
| `pydantic` | validation |
| `pydantic-settings` | environnement typé |
| `email-validator` | validation `EmailStr` |
| `python-jose[cryptography]` | JWT |
| `bcrypt` | mots de passe |
| `python-multipart` | formulaires et fichiers |
| `httpx` | client HTTP et TestClient |
| `python-dotenv` | lecture `.env` |
| `authlib` | Google OIDC |
| `itsdangerous` | signature des sessions Starlette |
| `pytest` | tests |
| `ruff` | lint |

Tous ces paquets ne correspondent pas aux lignes métier personnelles de Yanis, mais il a posé le
contrat d’installation du backend pour l’équipe.

Limite : outils de développement et dépendances de production sont mélangés.

## `start.ps1`

[Lignes 1 à 28](https://github.com/AshDv/ScribeProject/blob/2646623fc7c4bf83106cc4629ffa934131303012/start.ps1#L1-L28)

### Variables de chemin

```powershell
$ErrorActionPreference = "Stop"
$projectRoot = $PSScriptRoot
$serverPath = Join-Path $projectRoot "server"
$webPath = Join-Path $projectRoot "web"
$pythonPath = Join-Path $serverPath ".venv\Scripts\python.exe"
```

- toute erreur PowerShell arrête le script ;
- `$PSScriptRoot` est le dossier du script ;
- `Join-Path` évite de concaténer manuellement les séparateurs ;
- les noms sont en camelCase, convention PowerShell courante.

### Environnement Python

```powershell
if (-not (Test-Path $pythonPath)) {
  python -m venv ...
}
```

Le venv n’est créé que si son Python manque.

```powershell
& $pythonPath -m pip install -r ...
```

`&` exécute le chemin contenu dans la variable. `-m pip` garantit que pip appartient au Python du
venv.

### `.env`

Le script copie l’exemple uniquement si le vrai fichier manque. Il ne l’écrase donc pas.

### Frontend

`Push-Location` change temporairement de dossier, `npm install` installe, `Pop-Location` revient.

### Serveurs

Deux `Start-Process` ouvrent :

- Uvicorn sur 8000 avec rechargement ;
- Vite sur 5174.

`--reload` surveille les fichiers, utile en développement mais pas en production.

`Start-Sleep -Seconds 5` est un délai fixe avant l’ouverture du navigateur. Il ne vérifie pas
réellement que les serveurs sont prêts.

Limites :

- Windows seulement ;
- pas de contrôle de version Node ;
- `npm install` au lieu de `npm ci` ;
- installations répétées ;
- fenêtres séparées difficiles à arrêter proprement ;
- pas de gestion d’un port occupé ;
- a causé le problème Vite avec Node 20.11, car Vite 7 demande une version plus récente.

# 22. COMMIT 2 ligne par ligne — SQLModel et FastAPI

[Commit complet](https://github.com/AshDv/ScribeProject/commit/452b4ff60921cba714272cecdb51713c3d65385a)

## `server/app/db.py`

[Lignes 1 à 22](https://github.com/AshDv/ScribeProject/blob/452b4ff60921cba714272cecdb51713c3d65385a/server/app/db.py#L1-L22)

### Imports

```python
from __future__ import annotations
```

Reportait l’évaluation de certaines annotations et simplifiait les références de types. En Python
3.12, plusieurs usages modernes sont déjà disponibles, mais cette ligne reste compatible.

```python
from collections.abc import Generator
```

`Generator` décrit la fonction qui produit une session avec `yield`.

```python
from sqlmodel import Session, SQLModel, create_engine
```

- `Session` : unité de travail ;
- `SQLModel` : classe de base et métadonnées ;
- `create_engine` : crée l’accès à la base.

### Arguments SQLite

```python
_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
```

- le préfixe `_` indique une variable interne au module ;
- le dictionnaire désactive une restriction SQLite nécessaire dans le contexte multithread du
  serveur ;
- pour une autre base, le dictionnaire reste vide.

Cela ne rend pas SQLite adaptée à plusieurs serveurs ni à une forte écriture concurrente.

### Moteur

```python
engine = create_engine(settings.database_url, echo=False, connect_args=_args)
```

- `database_url` choisit la base ;
- `echo=False` évite d’imprimer chaque SQL ;
- `connect_args` transmet l’option SQLite ;
- `engine` est partagé par les sessions.

### Initialisation

```python
def init_db() -> None:
    from app import models  # noqa: F401
    SQLModel.metadata.create_all(engine)
```

L’import à l’intérieur garantit que les classes de tables sont enregistrées dans les métadonnées.
`# noqa: F401` dit à Ruff que l’import apparemment inutilisé a un effet nécessaire.

`create_all` crée les tables manquantes. Il ne sait pas migrer correctement une colonne existante.
La production demanderait Alembic.

### Session par requête

```python
def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
```

L’annotation du générateur représente :

- valeur produite : `Session` ;
- valeur envoyée dans le générateur : `None` ;
- valeur finale retournée : `None`.

FastAPI prend la session produite et la ferme après la requête grâce au `with`.

## `server/app/main.py`

[Lignes 1 à 38](https://github.com/AshDv/ScribeProject/blob/452b4ff60921cba714272cecdb51713c3d65385a/server/app/main.py#L1-L38)

### `asynccontextmanager`

Ce décorateur transforme un générateur asynchrone en gestionnaire de contexte.

```python
@asynccontextmanager
async def lifespan(_: FastAPI):
    settings.audio_directory.mkdir(parents=True, exist_ok=True)
    init_db()
    yield
```

- `_` reçoit l’application mais n’est pas utilisée ;
- `mkdir(parents=True)` crée les parents ;
- `exist_ok=True` évite une erreur si le dossier existe ;
- `init_db()` prépare les tables ;
- le code avant `yield` s’exécute au démarrage ;
- le code après `yield`, absent ici, s’exécuterait à l’arrêt.

### Instance FastAPI

```python
app = FastAPI(title="Scribe API", version="1.0.0", lifespan=lifespan)
```

`app` est l’instance ASGI chargée par Uvicorn avec `app.main:app`.

### `SessionMiddleware`

```python
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.secret_key,
    same_site="lax",
    https_only=settings.environment == "production",
)
```

Il ajoute une session signée, notamment pour l’état temporaire Google OAuth.

- `same_site="lax"` réduit l’envoi de cookie dans certains contextes intersites ;
- `https_only` active le drapeau Secure en production.

Ce middleware ne remplace pas le JWT de l’API.

### CORS

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

- seules les origines listées peuvent lire les réponses dans le navigateur ;
- credentials autorise certains en-têtes/cookies ;
- seuls les verbes utilisés sont annoncés ;
- seuls Bearer et Content-Type sont nécessaires.

CORS n’est pas un pare-feu et ne bloque pas un script serveur.

### Route de santé

```python
@app.get("/api/health")
def health():
    return {"status": "ok"}
```

- le décorateur associe URL et verbe ;
- `health` est une fonction sans paramètre ;
- le dictionnaire est automatiquement sérialisé en JSON.

Le check prouve que le processus répond. Il ne teste pas Mistral, SMTP ou Google.

# 23. COMMIT 3 ligne par ligne — React et Vite

[Commit complet](https://github.com/AshDv/ScribeProject/commit/ed08945d27613f7d2942baf3e482465483e338bb)

## `web/index.html`

[Lignes 1 à 14](https://github.com/AshDv/ScribeProject/blob/ed08945d27613f7d2942baf3e482465483e338bb/web/index.html#L1-L14)

| Ligne | Explication |
|---|---|
| `<!doctype html>` | active le standard HTML5 |
| `<html lang="fr">` | langue principale pour accessibilité |
| `<head>` | métadonnées invisibles principales |
| `charset="UTF-8"` | accents et caractères Unicode |
| `viewport` | largeur adaptée aux téléphones |
| `theme-color` | couleur possible de l’interface du navigateur |
| `description` | résumé pour aperçu et moteurs |
| `<title>` | titre d’onglet |
| `<body>` | contenu visible |
| `<div id="root">` | point de montage React |
| `type="module"` | script ECMAScript module |
| `src="/src/main.jsx"` | point d’entrée géré par Vite |

Le HTML ne contient presque aucune interface, car React la construit dans `root`.

## `web/package.json`

[Lignes 1 à 19](https://github.com/AshDv/ScribeProject/blob/ed08945d27613f7d2942baf3e482465483e338bb/web/package.json#L1-L19)

- `name` identifie le paquet.
- `private: true` empêche une publication npm accidentelle.
- `version` documente la version applicative.
- `type: "module"` active `import`/`export`.

Scripts :

- `npm run dev` lance Vite ;
- `npm run build` produit `dist` ;
- `npm run preview` sert localement le build.

Dépendances runtime :

- `react` ;
- `react-dom`.

Dépendances de développement :

- plugin React pour Vite ;
- Vite.

Le caret `^18.3.1` autorise certaines mises à jour compatibles lors d’une nouvelle résolution.
`package-lock.json` fixe ensuite la résolution exacte installée.

## `package-lock.json`

Ce fichier de 1 802 lignes a été généré par npm.

Il enregistre :

- version exacte ;
- URL du paquet ;
- empreinte d’intégrité ;
- dépendances indirectes ;
- contraintes Node.

Yanis doit savoir expliquer le fichier mais ne doit pas prétendre avoir rédigé chaque ligne.

L’erreur de démonstration avec Node 20.11 venait de Vite 7. Le projet aurait dû documenter ou
contrôler Node 20.19+ ou 22.12+.

## `web/src/main.jsx`

[Lignes 1 à 10](https://github.com/AshDv/ScribeProject/blob/ed08945d27613f7d2942baf3e482465483e338bb/web/src/main.jsx#L1-L10)

```javascript
import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App.jsx";
import "./index.css";
```

- React fournit `StrictMode` ;
- ReactDOM manipule le DOM navigateur ;
- `App` est le composant racine ;
- l’import CSS demande à Vite d’inclure les styles.

```javascript
ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

- `document.getElementById` récupère le div HTML ;
- `createRoot` crée une racine React moderne ;
- `render` affiche l’arbre ;
- `StrictMode` déclenche des vérifications supplémentaires en développement et peut réexécuter
  certains cycles pour révéler les effets mal nettoyés ;
- cela ne double pas l’interface en production.

## `web/vite.config.js`

[Lignes 1 à 12](https://github.com/AshDv/ScribeProject/blob/ed08945d27613f7d2942baf3e482465483e338bb/web/vite.config.js#L1-L12)

```javascript
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
```

`defineConfig` aide l’éditeur et le typage de configuration. Le plugin transforme JSX et active
l’actualisation React.

```javascript
export default defineConfig({
  plugins: [react()],
```

L’objet exporté est lu par Vite. `react()` construit l’instance du plugin.

```javascript
server: {
  port: 5174,
  strictPort: true,
  proxy: { "/api": "http://localhost:8000" },
}
```

- port choisi pour le frontend ;
- `strictPort` échoue au lieu de changer silencieusement ;
- le proxy transmet `/api` au backend local.

Le navigateur croit appeler la même origine Vite. Le proxy évite de coder `localhost:8000` dans
chaque composant.

Ce proxy ne s’applique qu’au serveur de développement. Le déploiement doit configurer un domaine,
un reverse proxy ou une URL d’API.

# 24. COMMIT 4 ligne par ligne — coquille React et CSS

[Commit complet](https://github.com/AshDv/ScribeProject/commit/6104ac55c5dad4fe4b6d7382a7ea5d17c9862250)

## `web/src/App.jsx` initial

[Lignes 1 à 7](https://github.com/AshDv/ScribeProject/blob/6104ac55c5dad4fe4b6d7382a7ea5d17c9862250/web/src/App.jsx#L1-L7)

```javascript
export default function App() {
```

- export par défaut : un seul composant principal par fichier ;
- nom en PascalCase obligatoire pour un composant JSX ;
- aucune prop à ce stade.

Le `return` renvoie :

- `<main>` comme contenu principal ;
- `<section>` comme carte ;
- bloc de marque ;
- titre unique ;
- texte d’état.

`className` associe les classes CSS. Les éléments sont imbriqués comme un arbre.

## `web/src/index.css`

[Voir les 90 lignes initiales](https://github.com/AshDv/ScribeProject/blob/6104ac55c5dad4fe4b6d7382a7ea5d17c9862250/web/src/index.css#L1-L90)

Le fichier met beaucoup de propriétés sur une même ligne. Cela réduit le nombre physique de lignes,
mais pas la quantité de code. Pour la maintenance, un formateur CSS serait préférable.

## Lecture de chaque famille de sélecteurs

| Sélecteurs | Rôle |
|---|---|
| `@import` | charge DM Sans et Manrope depuis Google |
| `:root` | typographie, couleurs globales et variables |
| `*` | applique `box-sizing: border-box` partout |
| `body` | retire marge, impose hauteur et fond |
| `button,input` | hérite de la police |
| `.app-shell` | grille barre latérale + contenu |
| `.sidebar` | navigation sombre et fixe |
| `.brand`, `.brand-mark` | identité visuelle |
| `.nav-list`, `.nav-button` | navigation et états hover/actif |
| `.profile-card`, `.avatar` | profil utilisateur |
| `.main-content`, `.page` | conteneur et animation d’entrée |
| `.page-header` | titre et actions d’une page |
| `.eyebrow`, `.card-label` | petit libellé uppercase |
| `.secure-badge` | badge de sécurité |
| `.recorder-grid` | disposition dictaphone + explication |
| `.recorder-card` | carte principale |
| `.orb`, `.orb.live` | cercle et animation d’enregistrement |
| `.timer` | chronomètre |
| `.record-button` | action de démarrage |
| `.primary-button` | action principale |
| `.secondary-button` | action secondaire |
| `.stop-button` | action destructive/arrêt |
| `.control-row` | groupe flexible de boutons |
| `.audio-player` | lecteur audio |
| `.spinner` | indicateur de chargement |
| `.steps-card`, `.step` | étapes d’utilisation |
| `.consent` | encadré de consentement |
| `.alert.error`, `.alert.success` | retour d’erreur ou succès |
| `.auth-layout` | grille de connexion |
| `.auth-story`, `.auth-panel` | colonne marketing et formulaire |
| `.google-button` | SSO Google |
| `.separator` | séparation visuelle |
| `.auth-form`, `.field` | formulaire et champs |
| `.recording-list`, `.recording-row` | bibliothèque des résultats |
| `.status.*` | statuts colorés |
| `.result-grid` | cartes du compte rendu |
| `.topics` | étiquettes de sujets |
| `.privacy-grid` | informations RGPD |
| `.meeting-form` | préparation de réunion |
| `.participant-fields` | champs dynamiques |
| `.consent-dashboard` | suivi des accords |
| `.public-page`, `.public-card` | page accessible par token |
| `@media max-width:900px` | tablette et navigation compacte |
| `@media max-width:560px` | téléphone |

## Propriétés CSS à connaître

| Propriété | Signification |
|---|---|
| `margin` | espace extérieur |
| `padding` | espace intérieur |
| `width`, `height` | dimensions |
| `min-*`, `max-*` | bornes de dimensions |
| `display:flex` | disposition flexible |
| `display:grid` | grille |
| `gap` | espace entre enfants |
| `align-items` | alignement transversal |
| `justify-content` | alignement principal |
| `flex-direction` | axe ligne ou colonne |
| `grid-template-columns` | colonnes de grille |
| `position:sticky` | reste visible selon le défilement |
| `position:relative/absolute` | repère et positionnement |
| `top`, `right`, `bottom` | décalages |
| `overflow:hidden` | masque les débordements |
| `border` | contour |
| `border-radius` | coins arrondis |
| `box-shadow` | ombre |
| `background` | couleur, image ou gradient |
| `color` | couleur du texte |
| `font` | raccourci typographique |
| `font-weight` | graisse |
| `letter-spacing` | espacement des lettres |
| `line-height` | hauteur de ligne |
| `text-transform` | majuscules visuelles |
| `text-overflow:ellipsis` | points de suspension |
| `white-space:nowrap` | empêche le retour |
| `cursor:pointer` | curseur d’action |
| `transition` | interpolation d’un changement |
| `transform` | déplacement/rotation |
| `animation` | animation nommée |
| `opacity` | transparence |
| `accent-color` | couleur native checkbox |
| `object-fit` | adaptation d’un média, non utilisé ici |

## Unités

- `px` : pixel CSS ;
- `%` : proportion du parent ;
- `vh` : pourcentage de hauteur de viewport ;
- `fr` : fraction de grille ;
- `rem` : taille relative à la racine, peu utilisée ici ;
- `clamp(min, idéal, max)` : taille responsive bornée ;
- `minmax` : borne une piste Grid.

## Pseudo-classes et pseudo-éléments

- `:hover` : pointeur au-dessus ;
- `:focus` : élément focalisé ;
- `:disabled` : bouton désactivé ;
- `:before`, `:after` : contenu visuel généré ;
- `>div` : enfant direct ;
- `.a.b` : élément possédant les deux classes.

## Animations

`@keyframes enter`, `pulse` et `spin` définissent les étapes. L’animation de pulse signale
l’enregistrement ; le spinner signale l’attente.

Une interface accessible devrait respecter :

```css
@media (prefers-reduced-motion: reduce)
```

Cette règle manque.

## Point d’atomicité

Le fichier contient des styles pour des écrans ajoutés dans des commits ultérieurs. Le choix
prépare un design system cohérent, mais rend le commit « application shell » plus large que son JSX
visible.

Phrase à dire :

> J’ai posé le système visuel complet très tôt pour éviter des styles incohérents. Avec plus de
> recul, j’aurais séparé les tokens et composants génériques des styles propres aux fonctionnalités
> afin d’obtenir des commits encore plus atomiques.

# 25. COMMIT 5 ligne par ligne — accord, retrait et effacement

[Commit complet](https://github.com/AshDv/ScribeProject/commit/4e21df68d3c0241f1ca5d9b9751e8aeaf5315daa)

Le début de `consent_routes.py`, écrit auparavant par l’équipe, contient déjà la création des
invitations. Le code propre à ce commit commence principalement au démarrage de la réunion.

[Voir le fichier à l’état du commit](https://github.com/AshDv/ScribeProject/blob/4e21df68d3c0241f1ca5d9b9751e8aeaf5315daa/server/app/consent_routes.py)

## Imports ajoutés ou utilisés

```python
import hashlib
import secrets
from pathlib import Path
```

- `hashlib` fournit SHA-256 ;
- `secrets` génère des tokens cryptographiquement aléatoires ;
- `Path` sert à vérifier et supprimer les fichiers audio.

Les modèles importés décrivent les tables modifiées ou supprimées.

## `token_hash`

```python
def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()
```

Étape par étape :

1. `token` est une chaîne secrète présente dans le lien.
2. `encode()` la convertit en octets UTF-8.
3. `sha256` calcule une empreinte de 256 bits.
4. `hexdigest()` l’écrit sous forme de 64 caractères hexadécimaux.

Pourquoi SHA-256 ici et bcrypt pour les mots de passe :

- le token est généré avec beaucoup d’entropie, pas choisi par un humain ;
- on doit retrouver rapidement sa ligne par égalité ;
- bcrypt serait inutilement coûteux et compliquerait l’indexation ;
- un mot de passe humain est faible, donc exige une fonction lente et salée.

Il ne faut pas dire « SHA-256 crée l’empreinte d’un utilisateur ». Ici, il crée l’empreinte d’un
token de consentement.

## `owned_session`

```python
meeting = db.get(ConsentSession, session_id)
if not meeting or meeting.owner_id != user.id:
    raise HTTPException(404, "Réunion introuvable")
return meeting
```

- `db.get` cherche par clé primaire ;
- la condition traite absence et mauvais propriétaire ;
- 404 masque l’existence à un tiers ;
- la fonction renvoie une instance vérifiée.

Le nom `owned_session` exprime qu’elle ne récupère pas seulement une réunion : elle garantit la
propriété.

## `participants_for`

La fonction construit une requête :

```python
select(ParticipantConsent).where(ParticipantConsent.session_id == session_id)
```

`db.exec` l’exécute. `list(...)` matérialise les résultats afin de pouvoir les parcourir plusieurs
fois et tester leur présence.

## `is_active`

```python
return bool(consent.consented_at and not consent.withdrawn_at)
```

Un consentement est actif seulement si :

- une date d’accord existe ;
- aucune date de retrait n’existe.

`bool` force une vraie valeur booléenne au lieu de renvoyer éventuellement un objet `datetime`.

## `refresh_status`

La fonction recalcule l’état à partir des données :

- si la réunion enregistre déjà, elle ne change pas automatiquement ;
- si la liste est non vide et tous les accords sont actifs : `READY` ;
- sinon : `PENDING`.

```python
all(is_active(item) for item in participants)
```

`all` renvoie vrai si tous les éléments sont vrais. Sur une collection vide, `all` renvoie vrai par
définition ; c’est pourquoi `participants and ...` est indispensable.

`db.add(meeting)` signale l’objet modifié. Le commit est laissé à la route appelante pour éviter des
transactions cachées dans chaque helper.

## `session_detail`

Cette fonction construit un dictionnaire de réponse. Elle évite :

- d’exposer automatiquement toutes les colonnes ;
- de répéter le même format dans plusieurs routes ;
- de laisser le frontend deviner l’état.

La compréhension de liste transforme chaque objet de base en petit dictionnaire public.

## `start_session`

[Bloc correspondant](https://github.com/AshDv/ScribeProject/blob/4e21df68d3c0241f1ca5d9b9751e8aeaf5315daa/server/app/consent_routes.py#L165-L184)

### Décorateur

```python
@router.post("/consent-sessions/{session_id}/start")
```

`{session_id}` est un paramètre dynamique extrait de l’URL. `POST` est choisi, car démarrer modifie
l’état.

### Signature

```python
def start_session(
    session_id: str,
    payload: StartInput,
    user: User = Depends(current_user),
    db: Session = Depends(get_session),
):
```

- `session_id` vient du chemin ;
- `payload` vient du JSON ;
- `user` est injecté après vérification JWT ;
- `db` est injectée et fermée après la requête.

### Contrôles

```python
meeting = owned_session(session_id, user, db)
```

Empêche de démarrer la réunion d’autrui.

```python
if not payload.notice_confirmed:
```

Exige que l’organisateur confirme l’annonce orale aux personnes présentes.

```python
if not participants or not all(...):
```

Bloque si une personne manque ou a retiré son accord. Le backend refait le contrôle, même si le
bouton React est désactivé.

### Changement d’état

```python
meeting.status = ConsentSessionStatus.RECORDING
meeting.notice_confirmed_at = utc_now()
meeting.started_at = utc_now()
```

Les enums évitent les fautes de chaîne. UTC donne une chronologie indépendante du fuseau.

Deux appels séparés à `utc_now()` peuvent différer de quelques microsecondes. Une seule variable
`now = utc_now()` serait plus cohérente si les dates doivent être identiques.

## `stop_session`

[Bloc correspondant](https://github.com/AshDv/ScribeProject/blob/4e21df68d3c0241f1ca5d9b9751e8aeaf5315daa/server/app/consent_routes.py#L186-L198)

La route appartient à l’organisateur authentifié. Elle place :

- état `STOPPED` ;
- date d’arrêt ;
- puis valide.

Elle est idempotente au sens pratique : la rappeler laisse l’état arrêté, mais met à jour la date.
Une idempotence stricte conserverait la première date.

## `public_consent`

```python
select(ParticipantConsent).where(
    ParticipantConsent.token_hash == token_hash(token)
)
```

Le token en clair arrive par l’URL. Le serveur calcule son hash et compare au hash stocké.

Le lien public fonctionne comme un Bearer token : toute personne qui le possède peut agir. Il doit
donc être :

- suffisamment aléatoire ;
- transmis par un canal contrôlé ;
- non journalisé inutilement ;
- expirant dans une version de production.

Le code ne définit actuellement aucune expiration du token.

## `get_public_consent`

[Bloc correspondant](https://github.com/AshDv/ScribeProject/blob/4e21df68d3c0241f1ca5d9b9751e8aeaf5315daa/server/app/consent_routes.py#L209-L223)

La route n’exige pas de compte, car un invité peut ne pas être utilisateur Scribe.

Elle renvoie seulement les informations nécessaires :

- nom ;
- réunion ;
- état d’accord ;
- version de notice ;
- sous-traitant ;
- contact ;
- durée.

Elle ne renvoie ni hash, ni e-mail, ni ID interne du compte.

## `accept_consent`

[Bloc correspondant](https://github.com/AshDv/ScribeProject/blob/4e21df68d3c0241f1ca5d9b9751e8aeaf5315daa/server/app/consent_routes.py#L225-L236)

```python
consent.consented_at = utc_now()
consent.withdrawn_at = None
```

L’accord pose une date et annule un ancien retrait. Le code autorise donc une personne à consentir
de nouveau via le même lien tant que le token existe.

La réunion associée est recalculée. Le commit persiste consentement et statut dans la même
transaction.

Limite : rappeler l’endpoint change la date d’accord, donc ce n’est pas strictement idempotent.

## `withdraw_consent`

[Bloc correspondant](https://github.com/AshDv/ScribeProject/blob/4e21df68d3c0241f1ca5d9b9751e8aeaf5315daa/server/app/consent_routes.py#L238-L250)

Le retrait :

1. pose `withdrawn_at` ;
2. récupère la réunion ;
3. arrête immédiatement son état serveur ;
4. pose `stopped_at` ;
5. valide ensemble.

Le navigateur ne reçoit pas un push instantané. Il interroge le serveur toutes les trois secondes.
Le terme « immédiatement » concerne la règle serveur, pas la détection réseau à la milliseconde.

## `erase_consent_data`

[Bloc correspondant](https://github.com/AshDv/ScribeProject/blob/4e21df68d3c0241f1ca5d9b9751e8aeaf5315daa/server/app/consent_routes.py#L252-L280)

### Relations

Le serveur retrouve tous les `SessionRecording` de la réunion. Pour chaque lien :

- il charge l’enregistrement ;
- vérifie le chemin ;
- supprime l’audio ;
- supprime le rapport ;
- supprime l’enregistrement ;
- supprime la liaison.

### Contrôle de chemin

```python
path = Path(recording.audio_path).resolve()
if recording.audio_path and path.is_relative_to(settings.audio_directory) and path.exists():
    path.unlink()
```

Les trois contrôles empêchent :

- le chemin vide ;
- la sortie du dossier autorisé ;
- l’erreur si le fichier manque.

### Anonymisation et révocation du lien

```python
consent.name = "Données effacées"
consent.email = ""
consent.token_hash = token_hash(secrets.token_urlsafe(32))
consent.erasure_requested_at = utc_now()
```

- identité effacée ;
- token remplacé par un hash aléatoire inconnu ;
- ancien lien rendu invalide ;
- date de demande conservée.

### Limite critique

Une seule personne possédant son lien peut déclencher la suppression de **tous les enregistrements
liés à la réunion**, pas seulement de ses propres données.

Cela répond agressivement au retrait, mais peut supprimer les données des autres participants et de
l’organisateur. Une version de production doit définir la règle juridique et technique :

- arrêter et marquer la réunion ;
- supprimer ou rendre inaccessible le passage concerné si possible ;
- demander une validation de l’organisateur ou d’un workflow RGPD ;
- journaliser la demande ;
- éviter qu’un lien public sans expiration produise une destruction globale immédiate.

Autres limites :

- aucune confirmation ;
- aucune expiration ;
- aucune protection contre plusieurs appels concurrents ;
- fichiers supprimés hors transaction SQL ;
- absence de tâche de reprise ;
- token dans URL pouvant apparaître dans l’historique.

# 26. COMMIT 6 ligne par ligne — interface publique de consentement

[Commit complet](https://github.com/AshDv/ScribeProject/commit/ecd894ce955b396193fcc1300278517fbd4c3d35)

## `PublicConsent`

[Lignes 1 à 52](https://github.com/AshDv/ScribeProject/blob/ecd894ce955b396193fcc1300278517fbd4c3d35/web/src/PrivacyFlows.jsx#L1-L52)

### Imports

```javascript
import { useEffect, useState } from "react";
import { api } from "./api";
```

React fournit les hooks ; `api` centralise HTTP.

### Signature

```javascript
export function PublicConsent({ token }) {
```

- export nommé : d’autres modules importent précisément ce composant ;
- `token` est extrait des props ;
- le composant n’a pas besoin de connaître tout le routeur.

### États

```javascript
const [notice, setNotice] = useState(null);
const [message, setMessage] = useState("");
const [error, setError] = useState("");
```

- `notice` : données serveur ou `null` pendant le chargement ;
- `message` : confirmation métier ;
- `error` : erreur séparée du succès.

Des états séparés rendent les transitions explicites.

### Chargement

```javascript
useEffect(() => {
  api.getPublicConsent(token)
    .then(setNotice)
    .catch((requestError) => setError(requestError.message));
}, [token]);
```

L’effet se relance si le token change.

- `.then(setNotice)` passe directement la réponse à la fonction ;
- `.catch` transforme l’erreur en message.

Il manque un mécanisme d’annulation si le composant disparaît avant la réponse.

### `act`

```javascript
async function act(action) {
```

`action` est elle-même une fonction, par exemple `api.acceptConsent`. C’est une fonction d’ordre
supérieur.

Elle :

1. efface l’erreur précédente ;
2. appelle l’action avec le token ;
3. choisit le message selon `response.status` ;
4. recharge l’état officiel ;
5. capture l’erreur.

Cette factorisation applique DRY aux boutons accepter et retirer.

### Retours anticipés

```javascript
if (error && !notice) return ...
if (!notice) return ...
```

Le premier affiche une erreur initiale. Le second affiche le chargement.

Un retour anticipé évite d’imbriquer toute l’interface dans un grand `if`.

### `active`

```javascript
const active = notice.consented_at && !notice.withdrawn_at;
```

La valeur peut techniquement être une chaîne de date ou une valeur falsy, pas forcément un booléen
strict. Dans une condition JSX cela fonctionne. `Boolean(...)` serait plus explicite.

### Liste de transparence

Les `<li>` décrivent :

- captation ;
- transfert ;
- diarisation ;
- résumé ;
- suppression audio ;
- durée ;
- retrait et effacement.

Le texte affiché doit rester synchronisé avec le traitement réel. Une simple phrase frontend n’est
pas une preuve.

### Boutons conditionnels

- non actif : accepter ;
- non actif sans retrait : refuser ;
- actif : retirer ;
- toujours : demander l’effacement.

Le refus et le retrait utilisent le même endpoint. Leur différence est l’état précédent et le
libellé.

### Confirmation d’effacement

```javascript
if (!confirm("...")) return;
```

`confirm` est une API native bloquante du navigateur. Simple pour le MVP, mais difficile à styliser
et tester.

L’appel `eraseConsentData` n’est pas dans un `try/catch` local. Une erreur peut donc devenir une
promesse rejetée sans message utilisateur propre.

## `PublicShell`

[Lignes 54 à 56](https://github.com/AshDv/ScribeProject/blob/ecd894ce955b396193fcc1300278517fbd4c3d35/web/src/PrivacyFlows.jsx#L54-L56)

`children` est une prop spéciale contenant le JSX placé entre les balises :

```jsx
<PublicShell>contenu</PublicShell>
```

Le composant factorise la page, la carte et la marque. Il applique DRY sans créer une abstraction
complexe.

## `LegalGate`

[Lignes 58 à 94](https://github.com/AshDv/ScribeProject/blob/ecd894ce955b396193fcc1300278517fbd4c3d35/web/src/PrivacyFlows.jsx#L58-L94)

Les deux états :

- `termsChecked` ;
- `privacyChecked`.

Ils sont séparés parce que les deux décisions ont un sens différent.

L’effet charge les notices une fois grâce au tableau vide.

`accept` appelle l’API puis `onAccepted`, callback du parent. Le composant ne choisit pas lui-même la
navigation suivante.

Les listes utilisent :

```javascript
notice.processing.map((item) => <li key={item}>{item}</li>)
```

`key` aide React à identifier chaque élément. Utiliser le texte comme clé suppose qu’il est unique.

Le bouton reste désactivé tant qu’une case manque. Le backend vérifie également.

Limite : `api.acceptLegal()` envoie toujours deux valeurs vraies ; il ne reçoit pas directement les
états. Le bouton garantit normalement leur présence dans l’UI, mais passer les valeurs serait un
contrat plus explicite.

## Méthodes ajoutées dans `api.js`

[Voir le diff](https://github.com/AshDv/ScribeProject/commit/ecd894ce955b396193fcc1300278517fbd4c3d35)

- `startConsentSession(id)` : POST avec confirmation de l’annonce ;
- `stopConsentSession(id)` : POST d’arrêt ;
- `getPublicConsent(token)` : GET public ;
- `acceptConsent(token)` : POST ;
- `withdrawConsent(token)` : POST ;
- `eraseConsentData(token)` : DELETE.

Les templates literals insèrent l’ID ou le token dans l’URL.

Limite générale : un token placé dans le chemin peut être journalisé par le serveur ou le proxy. Le
hash protège la base, pas les journaux contenant l’URL reçue.

# 27. COMMIT 7 ligne par ligne — upload audio sécurisé

[Commit complet](https://github.com/AshDv/ScribeProject/commit/2a1dbd0cc227d07739776329f5f517473913f15c)

[Voir `routes.py` à l’état du commit](https://github.com/AshDv/ScribeProject/blob/2a1dbd0cc227d07739776329f5f517473913f15c/server/app/routes.py)

## `ALLOWED_AUDIO`

Le dictionnaire associe un type MIME à une extension autorisée :

```python
"audio/webm": ".webm"
```

Pourquoi dictionnaire et non deux listes :

- une seule recherche donne l’autorisation et l’extension ;
- impossible de désynchroniser facilement les positions ;
- complexité moyenne constante.

Les variantes `audio/wav` et `audio/x-wav` couvrent des navigateurs différents.

Limite : le type MIME vient du client et peut être falsifié. Il faut inspecter les octets, décoder
avec une bibliothèque contrôlée ou scanner le fichier en production.

## `CONSENT_VERSION`

```python
CONSENT_VERSION = "2026-07-26"
```

Constante en majuscules. Elle fige la version de preuve associée à l’enregistrement.

Limite : la version diffère des valeurs de configuration `2026-07-22`. Il faudrait une source
unique de vérité pour éviter la divergence.

## `owned_recording`

[Lignes 161 à 166 dans la version finale](https://github.com/AshDv/ScribeProject/blob/9040eef62c6f24454db4448c3d2e1b8d197c9010/server/app/routes.py#L161-L166)

Même principe que `owned_session` :

- charge ;
- vérifie le propriétaire ;
- renvoie 404 ;
- retourne l’objet sûr.

Le helper centralise une règle d’autorisation critique.

## `parse_json`

```python
def parse_json(value: str | None) -> list:
    return json.loads(value) if value else []
```

La base stocke plusieurs listes en texte JSON. Cette fonction :

- désérialise si le texte existe ;
- renvoie une liste vide sinon.

Limite : un JSON corrompu déclenche `JSONDecodeError` et provoque une erreur 500. Une validation ou
des colonnes JSON natives seraient plus robustes.

## `recording_detail`

[Lignes 172 à 208](https://github.com/AshDv/ScribeProject/blob/9040eef62c6f24454db4448c3d2e1b8d197c9010/server/app/routes.py#L172-L208)

### Paramètre optionnel

```python
session: Session | None = None
```

La fonction peut construire une réponse de base sans session, ou enrichir avec le rapport si elle
en reçoit une.

### Expression conditionnelle multiligne

Le bloc `report = (...)` exécute la requête seulement si `session` existe.

### Dictionnaire de base

Il expose les colonnes utiles. `segments_json`, `topics_json`, `decisions_json` et `actions_json`
sont reconvertis en listes.

### Rapport détaillé

Si la ligne `StructuredReport` existe, une clé `report` est ajoutée.

Cette construction manuelle contrôle le contrat API. Elle est répétitive mais explicite.

Limites :

- une requête supplémentaire par détail ;
- dictionnaires non déclarés comme modèles de réponse FastAPI ;
- aucune validation de sortie ;
- JSON texte.

## `create_recording`

[Lignes 211 à 262](https://github.com/AshDv/ScribeProject/blob/9040eef62c6f24454db4448c3d2e1b8d197c9010/server/app/routes.py#L211-L262)

### `status_code=202`

La requête enregistre le fichier et planifie le traitement. Le résultat final n’est pas encore prêt,
donc `202 Accepted` est plus précis que `201`.

### `async def`

La lecture de l’upload utilise `await`. FastAPI peut gérer l’attente sans bloquer le même flux
d’exécution.

### Paramètres injectés

- `BackgroundTasks` : liste de tâches à exécuter après la réponse ;
- `Form` : champs multipart ;
- `UploadFile` : fichier temporaire fourni par FastAPI ;
- `current_user` : utilisateur JWT ;
- `get_session` : base.

`Form(...)` et `File(...)` utilisent `...` pour signifier obligatoire.

### Contrôles de consentement

1. booléen local vrai ;
2. réunion existante et possédée ;
3. état `RECORDING` ;
4. liste non vide ;
5. accord actif de tous.

Le booléen envoyé par le client ne suffit jamais. La base est la source de vérité.

### Normalisation MIME

```python
content_type = (audio.content_type or "").split(";")[0].lower()
```

- valeur vide si absente ;
- retire un éventuel paramètre après `;` ;
- met en minuscules.

### Lecture limitée

```python
data = await audio.read(settings.max_audio_mb * 1024 * 1024 + 1)
```

Le serveur lit au maximum un octet de plus que la limite. Si cet octet existe, il sait que le fichier
est trop grand sans devoir charger davantage.

Pourquoi `1024 * 1024` : conversion MiB en octets.

Limite : tout le fichier autorisé reste chargé en mémoire. Avec plusieurs uploads de 50 MiB, la
mémoire peut exploser. La production doit streamer vers un stockage objet avec limite.

### Nom du fichier

```python
original_filename=f"recording{extension}"
```

Le nom fourni par l’utilisateur n’est pas réutilisé. Cela évite :

- traversée de chemin ;
- caractères problématiques ;
- fuite du nom local.

Le champ s’appelle cependant `original_filename` alors qu’il ne contient pas le vrai nom original.
Le nom du champ est donc trompeur.

### Chemin

```python
path = settings.audio_directory / f"{recording.id}{extension}"
```

L’ID UUID réduit les collisions. L’opérateur `/` de `Path` joint les segments.

### Base et liaison

Le code ajoute :

- `Recording` ;
- `SessionRecording`.

Puis commit et refresh.

### Tâche

```python
background_tasks.add_task(process_recording, recording.id)
```

FastAPI l’exécute après la réponse. Seul l’ID est passé, pas l’objet de session qui sera fermé.

Limite critique :

- tâche dans le même processus ;
- perdue en cas de crash ;
- non durable en serverless ;
- pas de retry ;
- pas de file ;
- déploiement multiple difficile.

Production : stockage objet + file managée + worker idempotent.

## Liste

[Lignes 265 à 273](https://github.com/AshDv/ScribeProject/blob/9040eef62c6f24454db4448c3d2e1b8d197c9010/server/app/routes.py#L265-L273)

La requête filtre par `owner_id`, trie du plus récent au plus ancien et renvoie une vue légère.

Pourquoi ne pas renvoyer la transcription complète dans la liste : réduire payload et données
exposées.

## Détail

[Lignes 276 à 282](https://github.com/AshDv/ScribeProject/blob/9040eef62c6f24454db4448c3d2e1b8d197c9010/server/app/routes.py#L276-L282)

Le helper d’autorisation est appelé avant la sérialisation.

## Suppression

[Lignes 285 à 306](https://github.com/AshDv/ScribeProject/blob/9040eef62c6f24454db4448c3d2e1b8d197c9010/server/app/routes.py#L285-L306)

Ordre :

1. vérifier le propriétaire ;
2. supprimer liaison ;
3. supprimer rapport ;
4. supprimer fichier dans le bon dossier ;
5. supprimer enregistrement ;
6. commit.

Limites :

- système de fichiers hors transaction ;
- `Path("")` se résout vers le répertoire courant, même si la vérification empêche normalement sa
  suppression ;
- aucune journalisation ;
- pas de suppression en stockage objet ;
- pas d’annulation d’une tâche IA déjà en cours.

# 28. COMMIT 8 ligne par ligne — dictaphone navigateur

[Commit complet](https://github.com/AshDv/ScribeProject/commit/1ae2765b1bb0b9d585757c781a44ff2f4fc5b428)

[Voir les 217 lignes du composant](https://github.com/AshDv/ScribeProject/blob/1ae2765b1bb0b9d585757c781a44ff2f4fc5b428/web/src/MeetingWorkflow.jsx#L1-L217)

## Imports

```javascript
import { useEffect, useRef, useState } from "react";
import { api } from "./api";
```

- état visible ;
- références impératives ;
- synchronisation avec systèmes extérieurs ;
- client HTTP.

## `formatTime`

```javascript
const formatTime = (seconds) =>
  `${String(Math.floor(seconds / 60)).padStart(2, "0")}:${String(seconds % 60).padStart(2, "0")}`;
```

Lecture de gauche à droite :

- `seconds / 60` calcule les minutes décimales ;
- `Math.floor` garde l’entier inférieur ;
- `String` convertit en texte ;
- `padStart(2, "0")` ajoute un zéro ;
- `% 60` calcule le reste pour les secondes ;
- la template literal assemble `MM:SS`.

À 125 secondes : `02:05`.

Limite : au-delà de 59 minutes, le résultat devient `60:00`, ce qui reste compréhensible mais ne
présente pas les heures.

## `MeetingWorkflow`

```javascript
export function MeetingWorkflow({ onCreated }) {
  const [meeting, setMeeting] = useState(null);
```

`meeting` pilote le sous-écran.

```javascript
if (!meeting) return <MeetingSetup ... />;
if (meeting.status !== "recording") return <ConsentStatus ... />;
return <Recorder ... />;
```

C’est un petit automate :

- aucune réunion ;
- attente des accords ;
- enregistrement.

Le callback `setMeeting` est directement passé comme `onCreated` ou `onChange`.

## `MeetingSetup` — états

```javascript
const [title, setTitle] = useState("Nouvelle réunion");
const [participants, setParticipants] = useState([{ name: "", email: "" }]);
const [error, setError] = useState("");
const [busy, setBusy] = useState(false);
```

- titre prêt à éditer ;
- au moins un participant ;
- message d’erreur ;
- blocage pendant l’envoi.

Le serveur impose aussi au moins un participant.

## `update`

```javascript
const update = (index, field, value) => {
  setParticipants((items) =>
    items.map((item, position) =>
      position === index ? { ...item, [field]: value } : item,
    ),
  );
};
```

Pourquoi la forme fonctionnelle `setParticipants((items) => ...)` :

- elle reçoit l’état le plus récent ;
- évite un état périmé lors de mises à jour rapprochées.

Pourquoi `map` :

- produit un nouveau tableau ;
- ne mute pas l’ancien ;
- remplace seulement l’objet ciblé.

Pourquoi `[field]` :

- même fonction pour `name` et `email`.

Limite : n’importe quelle chaîne pourrait devenir une propriété. Ici les appels sont contrôlés par
le composant ; TypeScript pourrait limiter `field` à `"name" | "email"`.

## `create`

`preventDefault` empêche le rechargement.

Le bloc :

```javascript
setBusy(true);
setError("");
try { ... } catch (...) { ... } finally { setBusy(false); }
```

garantit la fin de l’état occupé, succès ou erreur.

`await api.createConsentSession({ title, participants })` envoie un objet dont les noms correspondent
au contrat backend.

## Ajout d’un participant

```javascript
setParticipants([...participants, { name: "", email: "" }])
```

Un nouveau tableau est créé. Limite : la forme fonctionnelle serait plus sûre si plusieurs clics
très rapides sont regroupés.

## Suppression

```javascript
participants.filter((_, position) => position !== index)
```

- `_` indique que la valeur participant n’est pas utilisée ;
- `filter` garde toutes les positions sauf celle ciblée.

Le bouton est affiché seulement si la liste contient plus d’une personne.

## `key={index}`

React utilise la clé pour suivre les lignes. L’index fonctionne pour un petit formulaire, mais quand
on supprime une ligne, React peut réutiliser le DOM d’une autre position.

Amélioration : donner à chaque ligne un identifiant stable généré côté frontend.

## `aria-label`

Le libellé dynamique permet à un lecteur d’écran de distinguer les champs qui n’ont qu’un
placeholder.

## `ConsentStatus`

### États

- `notice` : confirmation de l’annonce orale ;
- `error` : refus de démarrage ou erreur API.

### Polling

```javascript
useEffect(() => {
  const refresh = async () => onChange(await api.getConsentSession(meeting.id));
  const timer = setInterval(() => refresh().catch(() => {}), 3000);
  return () => clearInterval(timer);
}, [meeting.id, onChange]);
```

Toutes les trois secondes :

1. GET de l’état ;
2. mise à jour chez le parent.

Le nettoyage annule la minuterie.

Pourquoi polling plutôt que WebSocket : plus simple pour le MVP.

Limites :

- jusqu’à trois secondes de retard ;
- appels même sans changement ;
- erreurs silencieusement ignorées ;
- si `onChange` change d’identité à chaque rendu, l’effet peut être recréé ; ici `setMeeting` de
  React est stable ;
- pas de rafraîchissement immédiat avant la première période.

## `start`

Le frontend bloque d’abord si l’annonce n’est pas cochée, puis le backend refait le contrôle.

Le bouton est désactivé avec `!meeting.all_consented`. Une personne malveillante peut retirer
`disabled` dans le navigateur ; cela n’aide pas, car le serveur refuse.

## `Recorder` — machine à états

Valeurs :

| État | Sens |
|---|---|
| `idle` | prêt, pas de captation |
| `recording` | microphone actif |
| `paused` | MediaRecorder suspendu |
| `ready` | Blob disponible localement |
| `uploading` | envoi au serveur |

Ces chaînes pourraient devenir une constante ou un enum TypeScript pour éviter une faute.

## États visibles

```javascript
const [seconds, setSeconds] = useState(0);
const [audioBlob, setAudioBlob] = useState(null);
const [audioUrl, setAudioUrl] = useState("");
const [error, setError] = useState("");
```

- compteur ;
- données binaires ;
- URL locale pour le lecteur ;
- erreur.

`Blob` représente des octets avec un type MIME. Il n’est pas encore un fichier stocké sur disque
serveur.

## Références

```javascript
const recorder = useRef(null);
const stream = useRef(null);
const chunks = useRef([]);
const consentRevoked = useRef(false);
```

Ces valeurs changent pendant les callbacks du navigateur sans devoir redessiner l’écran.

Pourquoi pas des variables normales : elles seraient recréées à chaque rendu.

Pourquoi pas `useState` :

- le rendu n’utilise pas directement chaque changement ;
- les callbacks ont besoin d’une référence stable ;
- stocker MediaRecorder dans l’état serait inutile.

## Chronomètre

L’effet n’existe que pendant `recording`.

```javascript
setSeconds((value) => value + 1)
```

La mise à jour fonctionnelle évite de capturer une ancienne valeur.

Le navigateur peut ralentir les timers en arrière-plan. Ce compteur donne une estimation UI, pas
la durée audio certifiée. La vraie durée devrait venir des métadonnées audio.

## Surveillance du retrait

L’effet fonctionne pendant `recording` et `paused`.

Il charge l’état officiel. Si la réunion n’est plus autorisée :

- drapeau de retrait ;
- arrêt du MediaRecorder ;
- suppression du Blob ;
- révocation de l’URL ;
- message.

Le chaînage optionnel évite une erreur si l’objet manque.

```javascript
setAudioUrl((currentUrl) => {
  if (currentUrl) URL.revokeObjectURL(currentUrl);
  return "";
});
```

La forme fonctionnelle obtient l’URL la plus récente et libère la mémoire.

Limite importante :

```javascript
verify().catch(() => {})
```

ignore une panne réseau. Le dictaphone peut continuer localement sans savoir que l’accord a changé.
Le backend revérifiera à l’upload, mais la captation locale a continué.

Production :

- WebSocket/SSE ;
- arrêt de sécurité après plusieurs échecs de vérification ;
- indicateur réseau ;
- règle claire fail-closed.

## Effet de nettoyage global

```javascript
useEffect(() => () => {
  stream.current?.getTracks().forEach((track) => track.stop());
  if (audioUrl) URL.revokeObjectURL(audioUrl);
}, [audioUrl]);
```

La fonction de l’effet retourne directement un cleanup.

- chaque piste microphone est arrêtée ;
- l’URL Blob est libérée.

Comme `audioUrl` est une dépendance, le cleanup précédent s’exécute lors d’un changement d’URL et
au démontage.

## `start`

### Autorisation microphone

```javascript
stream.current = await navigator.mediaDevices.getUserMedia({ audio: true });
```

Le navigateur affiche une permission. Cette API fonctionne normalement sur :

- HTTPS ;
- `localhost`.

Elle peut échouer si :

- permission refusée ;
- aucun microphone ;
- appareil utilisé ;
- contexte non sécurisé.

### MediaRecorder

```javascript
recorder.current = new MediaRecorder(stream.current);
```

`new` appelle le constructeur natif avec le flux.

Le navigateur choisit généralement le codec par défaut. Le code ne négocie pas
`MediaRecorder.isTypeSupported`.

### Morceaux

`ondataavailable` reçoit les blocs. `event.data.size` évite d’ajouter un morceau vide.

Le code appelle `recorder.current.start()` sans intervalle ; les navigateurs peuvent livrer surtout
un morceau à l’arrêt. Un `timeslice` pourrait produire des blocs réguliers.

### `onstop`

Si retrait :

- vide les morceaux ;
- ne produit pas de Blob ;
- revient à `idle` ;
- coupe le micro.

Sinon :

```javascript
new Blob(chunks.current, {
  type: recorder.current.mimeType || "audio/webm"
})
```

Les morceaux sont assemblés dans l’ordre.

`URL.createObjectURL(blob)` crée une URL locale comme `blob:...` pour `<audio>`.

Cette URL n’envoie rien au serveur.

## `pause`

Le même bouton :

- appelle `pause` si enregistrement ;
- appelle `resume` sinon ;
- synchronise l’état React.

Une divergence est possible si MediaRecorder échoue ou change d’état entre les deux. Des événements
`onpause`/`onresume` seraient plus robustes.

## `stop`

Le contrôle vérifie :

- objet présent ;
- état différent d’`inactive`.

L’appel déclenche ensuite `onstop`, qui construit le Blob.

## `reset`

La fonction :

- révoque l’URL ;
- efface les octets ;
- remet URL, timer, état et erreur.

Elle illustre le nettoyage d’une machine à états.

## `send`

Elle passe en `uploading`, construit l’appel API puis transmet l’ID créé au parent.

Le booléen `true` dans l’appel est une confirmation frontend. Le serveur consulte la base.

En cas d’erreur, le Blob reste disponible et l’utilisateur peut réessayer.

## JSX du dictaphone

### Classes dynamiques

```javascript
`orb ${state === "recording" ? "live" : ""}`
```

Ajoute l’animation seulement pendant l’enregistrement.

### Fragments

```jsx
<>
  <audio ... />
  <div ... />
</>
```

Un fragment groupe plusieurs enfants sans ajouter de div.

### Lecteur

`controls` demande les commandes natives. `src={audioUrl}` pointe vers le Blob local.

## Méthodes `api.js` ajoutées

[Voir le diff de `api.js`](https://github.com/AshDv/ScribeProject/commit/1ae2765b1bb0b9d585757c781a44ff2f4fc5b428)

### `listRecordings`

GET de la liste privée.

### `getRecording`

GET du détail par ID.

### `createRecording`

```javascript
const form = new FormData();
form.set("title", title);
form.set("consent", String(consent));
form.set("consent_session_id", consentSessionId);
form.set("audio", audio, `scribe-${Date.now()}.webm`);
```

- `FormData` produit du multipart ;
- booléen converti en texte ;
- noms exactement attendus par FastAPI ;
- nom client horodaté ;
- le navigateur choisit la boundary et le Content-Type.

Il ne faut pas ajouter manuellement `Content-Type: multipart/form-data`, car la boundary manquerait.
La fonction générique détecte `FormData`.

### `deleteRecording`

DELETE sur l’ID.

# 29. COMMIT 9 ligne par ligne — rapport structuré Mistral

[Commit complet](https://github.com/AshDv/ScribeProject/commit/1f88e83fc774214614d25ddcfb07ea9ae989a4f1)

[Voir les 166 lignes de `llm.py`](https://github.com/AshDv/ScribeProject/blob/1f88e83fc774214614d25ddcfb07ea9ae989a4f1/server/app/llm.py#L1-L166)

## Docstring

```python
"""Compte rendu fidèle et traçable avec Mistral Medium 3.5."""
```

Elle annonce l’intention, pas une garantie mathématique. « fidèle » dépend du contrôle et de la
qualité du modèle.

## Imports

```python
import json
from typing import Literal
import httpx
from pydantic import BaseModel, Field, ValidationError
```

- `json` sérialise le payload ;
- `Literal` ferme une liste de chaînes ;
- `httpx` appelle l’API ;
- Pydantic décrit et valide.

## `SummaryError`

```python
class SummaryError(RuntimeError):
    pass
```

La classe ne rajoute aucun comportement. Son type permet au pipeline de distinguer une erreur de
résumé d’une autre erreur Python.

`pass` est une instruction vide nécessaire pour un corps de classe valide.

## `Speaker`

```python
label: str
participant_name: str | None = None
confidence: Literal["explicit", "unknown"]
```

- `label` vient de la diarisation ;
- le nom peut manquer ;
- confiance volontairement binaire.

Le mot `confidence` ne représente pas un score numérique. Il indique seulement si le lien est
explicite ou inconnu.

## `KeyPoint`

- sujet court ;
- détail ;
- locuteurs concernés ;
- IDs sources.

Pourquoi `segment_ids` dans chaque objet : traçabilité et audit.

## `Decision`

- décision ;
- personnes qui décident ;
- justification facultative ;
- sources.

Si la justification n’est pas dite, `None`, donc JSON `null`.

## `ActionItem`

```python
task: str = Field(min_length=1, max_length=300)
```

La tâche ne peut être vide ni démesurée.

- `owner` facultatif ;
- `due_date` est une chaîne, pas encore une date validée ;
- priorité limitée ;
- sources obligatoires au niveau du type liste, mais la liste peut être vide.

Limites :

- format de date non imposé ;
- aucune longueur minimale sur plusieurs champs ;
- `segment_ids` pourrait être vide ;
- propriétaire non relié à un identifiant utilisateur.

## `OpenQuestion`

Question non résolue, responsable éventuel et sources.

## `Risk`

Risque, mitigation éventuelle, responsable éventuel et sources.

## `Coverage`

Chaque segment reçoit :

- ID ;
- classification parmi sept valeurs ;
- endroits où il est utilisé ;
- raison d’exclusion facultative.

Les catégories `social`, `filler`, `inaudible` permettent de couvrir sans forcer ces propos dans le
résumé.

## `MeetingSummary`

Objet racine :

- langue ;
- résumé exécutif limité à 4 000 caractères ;
- compte rendu limité à 12 000 ;
- toutes les collections.

Le type Pydantic sert trois fois :

1. documentation Python ;
2. génération JSON Schema ;
3. validation de la réponse.

## `SYSTEM_PROMPT`

Chaque règle répond à un risque :

| Règle | Risque |
|---|---|
| utiliser seulement les segments | hallucination |
| conserver dates/nombres/objections | résumé trop lisse |
| lier aux IDs | absence de preuve |
| couvrir chaque segment | oubli silencieux |
| ne pas répéter le filler | rapport illisible |
| action seulement explicite | fausse tâche |
| nom seulement après identification | fausse attribution |
| pas d’e-mail ni attribut sensible inféré | vie privée |
| langue dominante | cohérence |
| JSON Schema uniquement | parsing fragile |

Pourquoi le prompt est en anglais alors que la sortie peut être française : les instructions système
sont séparées de la langue de réunion et ordonnent de répondre dans la langue dominante.

Risque d’injection : la transcription est placée dans le message utilisateur sous forme JSON. Un
participant peut prononcer « ignore les instructions ». Le message système a une priorité supérieure,
mais ce n’est pas une garantie. Il faudrait aussi traiter explicitement la transcription comme
donnée non fiable.

## Signature `generate_summary`

```python
def generate_summary(
    transcript: str,
    segments: list[dict],
    participant_names: list[str],
) -> MeetingSummary:
```

Entrées :

- texte intégral ;
- objets segment ;
- contexte nominal.

Sortie :

- instance validée.

`list[dict]` reste vague. Un modèle Pydantic `Segment` serait plus précis.

## Vérification de clé

Le code échoue avant l’appel réseau avec un message de configuration.

Il ne journalise jamais la clé.

## `payload`

Le dictionnaire est séparé du prompt système. Les e-mails ne sont pas ajoutés ; seulement les noms.

Limite : un e-mail prononcé dans la transcription reste présent. La phrase « ne pas exposer
d’e-mail » demande au LLM de ne pas le reproduire, mais le sous-traitant reçoit quand même le texte.
Une étape de détection/redaction serait nécessaire si cette donnée ne doit pas être transmise.

## Schéma

```python
schema = MeetingSummary.model_json_schema()
```

Pydantic transforme les classes imbriquées en JSON Schema.

## Appel `httpx.post`

### URL

```python
f"{settings.mistral_base_url}/chat/completions"
```

F-string combinant base configurable et endpoint.

### En-tête

```python
"Authorization": f"Bearer {settings.mistral_api_key}"
```

La clé prouve au service quel compte/quota facture l’appel. HTTPS doit protéger le transport.

### Corps

- modèle configurable ;
- messages system et user ;
- température ;
- top_p ;
- effort ;
- filtre de sécurité ;
- format de réponse.

`json.dumps(..., ensure_ascii=False)` garde les caractères français lisibles au lieu de `\u00e9`.

### Schéma strict

```python
"response_format": {
    "type": "json_schema",
    "json_schema": {
        "name": "meeting_report",
        "schema": schema,
        "strict": True,
    },
}
```

Le nom identifie le format. `strict` demande au fournisseur de respecter le schéma.

La compatibilité exacte des paramètres `reasoning_effort`, `safe_prompt` et `json_schema` doit être
vérifiée avec le modèle réellement disponible. Un identifiant configuré ne garantit pas que tous
les paramètres sont acceptés.

### Timeout

240 secondes limite l’attente réseau. C’est long pour une requête Web directe, mais le traitement
est en arrière-plan.

Il n’y a pas de retry ; un retry doit être borné et idempotent pour ne pas multiplier les coûts.

## Erreurs réseau

```python
except httpx.HTTPError as exc:
    raise SummaryError(...) from exc
```

Capture erreurs HTTPX de transport, pas les statuts 4xx/5xx qui sont des réponses valides du point de
vue réseau.

## Statut HTTP

Tout statut supérieur ou égal à 400 devient erreur métier.

Limite : le corps Mistral, qui pourrait expliquer la cause, n’est pas conservé. C’est prudent pour
ne pas exposer de données, mais moins utile pour le diagnostic.

## Extraction

```python
response.json()["choices"][0]["message"]["content"]
```

Le code suppose la structure Chat Completions :

- objet JSON ;
- liste `choices` non vide ;
- premier choix ;
- message ;
- contenu.

Une clé absente devient `KeyError`. Une liste vide provoque `IndexError`, qui n’est pas capturée
dans ce bloc. C’est une limite réelle.

## Contenu sous forme de liste

Certains clients peuvent retourner des parties :

```python
content = "".join(
    part.get("text", "")
    for part in content
    if isinstance(part, dict) and part.get("type") == "text"
)
```

- filtre les dictionnaires texte ;
- récupère leur texte ;
- concatène.

## Validation

```python
result = MeetingSummary.model_validate_json(content)
```

Pydantic parse le texte JSON puis vérifie tous les modèles imbriqués.

Le `except` capture :

- clé manquante ;
- mauvais type ;
- validation Pydantic.

Il ne capture pas explicitement `IndexError`, ni toutes les erreurs possibles de JSON selon la
hiérarchie Pydantic.

## Couverture

```python
expected = {item["id"] for item in segments}
covered = [item.segment_id for item in result.coverage]
if set(covered) != expected or len(covered) != len(expected):
```

Le premier test vérifie le même ensemble. Le second détecte les doublons dans la couverture.

Limites :

- suppose que tous les segments d’entrée ont une clé `id` ;
- suppose les IDs d’entrée uniques ;
- ne vérifie pas que les `segment_ids` des décisions/actions existent ;
- ne vérifie pas la cohérence de `used_in` ;
- ne prouve pas la fidélité sémantique.

# 30. COMMIT 10 ligne par ligne — pipeline Voxtral vers Mistral

[Commit complet](https://github.com/AshDv/ScribeProject/commit/15511bdaf809f905b2a76ab273e9f2f2be256469)

[Voir les 120 lignes de `processing.py`](https://github.com/AshDv/ScribeProject/blob/15511bdaf809f905b2a76ab273e9f2f2be256469/server/app/processing.py#L1-L120)

## Responsabilité

Ce module n’implémente ni l’algorithme STT ni le LLM. Il orchestre :

```text
base -> audio -> Voxtral -> segments -> Mistral -> validation -> base -> suppression audio
```

## Imports

- `json` : stockage des structures ;
- `Path` : fichier ;
- `Session`, `select` : base ;
- `settings`, `engine` : infrastructure ;
- `SummaryError`, `generate_summary` : résumé ;
- modèles SQL ;
- `TranscriptionError`, `transcribe_audio` : transcription.

Les imports nommés rendent les dépendances du pipeline visibles.

## Signature

```python
def process_recording(recording_id: str) -> None:
```

Pourquoi seulement un ID :

- la session HTTP d’upload sera fermée ;
- l’objet pourrait devenir périmé ;
- le worker recharge la source de vérité.

## Session indépendante

```python
with Session(engine) as session:
```

La tâche ouvre sa propre unité de travail.

## Chargement et garde

```python
recording = session.get(Recording, recording_id)
if not recording or recording.status == RecordingStatus.PROCESSING:
    return
```

- enregistrement supprimé : rien à faire ;
- déjà en traitement : évite un doublon simple.

Limites :

- `COMPLETED` ou `FAILED` ne sont pas refusés et pourraient être retraités ;
- deux workers peuvent lire `UPLOADED` en même temps avant que l’un committe ;
- il faut un verrou ou une mise à jour atomique.

## Passage à `PROCESSING`

```python
recording.status = RecordingStatus.PROCESSING
recording.error = None
session.add(recording)
session.commit()
```

Le commit rapide rend le statut visible au frontend avant l’appel long. L’ancienne erreur est
effacée.

## Chemin et `link`

```python
path = Path(recording.audio_path).resolve()
link = None
```

`link` est initialisé avant `try` parce que `finally` doit pouvoir le tester même si la requête
échoue.

Le calcul de `path` est avant le `try`. Une exception à cet endroit ne serait donc pas transformée
en statut `FAILED` ni suivie du nettoyage prévu.

## Recherche de la liaison

La requête cherche la ligne unique associée à l’enregistrement.

Si elle manque, le traitement continue avec une liste de participants vide. Cela permet une certaine
tolérance, mais un enregistrement normalement conforme devrait avoir sa liaison.

## Expression conditionnelle des participants

```python
participants = (
    list(...)
    if link
    else []
)
```

Le format multiligne rend le ternaire complexe lisible.

## Noms

```python
names = [item.name for item in participants if item.name]
```

Les noms servent :

- de biais de contexte à Voxtral dans le module d’Ashwin ;
- de liste de participants au LLM.

Ils ne constituent pas une preuve que la voix correspond au nom.

## Transcription

```python
transcript = transcribe_audio(path, recording.content_type, names)
```

Entrées :

- chemin ;
- MIME ;
- vocabulaire.

Sortie attendue :

```python
{
    "text": "...",
    "diarized_text": "...",
    "segments": [...]
}
```

La fonction a été écrite par Ashwin. Yanis l’intègre et doit savoir expliquer son contrat, sans se
l’attribuer.

## Résumé

```python
result = generate_summary(transcript["text"], transcript["segments"], names)
```

Le rapport dépend de la transcription. Si Voxtral échoue, Mistral n’est pas appelé.

## Champs rapides du `Recording`

```python
recording.transcript = transcript["text"]
recording.segments_json = json.dumps(...)
recording.summary = result.executive_summary
```

Les champs principaux permettent d’afficher rapidement le résultat sans toujours joindre le rapport.

Les thèmes et décisions sont réduits à des listes de chaînes.

Les actions gardent leur objet complet via `model_dump`.

Pourquoi `ensure_ascii=False` : accents lisibles en base.

## `StructuredReport`

Une nouvelle instance reçoit tous les détails.

Pour chaque liste Pydantic :

```python
[item.model_dump() for item in result.speakers]
```

- `model_dump` transforme l’objet Pydantic en dictionnaire ;
- la compréhension transforme toute la liste ;
- `json.dumps` produit le texte stockable.

Pourquoi une table séparée :

- le `Recording` garde une vue rapide ;
- le rapport riche reste isolé ;
- relation un-à-un par `recording_id`.

Limite : le même contenu est dupliqué entre `Recording` et `StructuredReport`, ce qui peut diverger.

## Succès

```python
recording.status = RecordingStatus.COMPLETED
recording.completed_at = utc_now()
```

Le statut n’est marqué terminé qu’après construction du rapport.

## Erreurs capturées

```python
except (TranscriptionError, SummaryError, OSError) as exc:
```

Le pipeline transforme ces erreurs attendues en :

- statut `FAILED` ;
- message dans `recording.error`.

Il ne capture pas :

- erreur SQL ;
- `KeyError` inattendue dans le contrat transcription ;
- `IndexError` ;
- erreur de sérialisation inhabituelle.

Capturer toutes les exceptions pourrait empêcher le statut de rester bloqué, mais masquerait aussi
des bugs. Une solution de production journalise la trace, marque l’échec et alerte.

## `finally`

Ce bloc s’exécute après succès ou exception capturée.

### Suppression audio

```python
if path.is_relative_to(settings.audio_directory) and path.exists():
    path.unlink()
recording.audio_path = ""
```

L’audio est supprimé même si la transcription ou le résumé échoue.

Avantage :

- minimisation ;
- pas de conservation silencieuse.

Coût :

- impossible de réessayer sans redemander l’audio ;
- diagnostic plus difficile.

### Arrêt de réunion

Si la liaison existe, la réunion passe `STOPPED` avec une date.

## Commit final

```python
session.add(recording)
session.commit()
```

Il persiste :

- rapport ajouté ;
- champs de résultat ;
- statut ;
- réunion arrêtée.

Limite critique : l’audio est supprimé avant ce commit. Si le commit échoue, la base peut encore
indiquer un chemin vers un fichier disparu.

## Architecture de production proposée

```text
Upload direct vers stockage objet chiffré
    |
    v
Événement dans une file managée
    |
    v
Worker idempotent
    |
    +-- verrou / statut atomique
    +-- transcription
    +-- résumé validé
    +-- transaction DB
    `-- suppression objet avec reprise
```

Cette cible est compatible avec l’intention serverless. Le code actuel local ne l’est pas encore à
cause de SQLite, du disque et de `BackgroundTasks`.

---

# 31. Atlas GitHub : où aller quand le professeur demande « montre-moi »

## Fondation

| Sujet demandé | Lien exact |
|---|---|
| configuration | [`config.py` lignes 1–74](https://github.com/AshDv/ScribeProject/blob/9040eef62c6f24454db4448c3d2e1b8d197c9010/server/app/config.py#L1-L74) |
| variables attendues | [`.env.example`](https://github.com/AshDv/ScribeProject/blob/2646623fc7c4bf83106cc4629ffa934131303012/server/.env.example#L1-L32) |
| dépendances Python | [`requirements.txt`](https://github.com/AshDv/ScribeProject/blob/2646623fc7c4bf83106cc4629ffa934131303012/server/requirements.txt#L1-L15) |
| règles Ruff/Pytest | [`pyproject.toml`](https://github.com/AshDv/ScribeProject/blob/2646623fc7c4bf83106cc4629ffa934131303012/pyproject.toml#L1-L10) |
| script Windows | [`start.ps1`](https://github.com/AshDv/ScribeProject/blob/2646623fc7c4bf83106cc4629ffa934131303012/start.ps1#L1-L28) |
| moteur SQLModel | [`db.py`](https://github.com/AshDv/ScribeProject/blob/9040eef62c6f24454db4448c3d2e1b8d197c9010/server/app/db.py#L1-L22) |
| démarrage FastAPI | [`main.py`](https://github.com/AshDv/ScribeProject/blob/9040eef62c6f24454db4448c3d2e1b8d197c9010/server/app/main.py#L1-L44) |

## Frontend

| Sujet demandé | Lien exact |
|---|---|
| HTML racine | [`index.html`](https://github.com/AshDv/ScribeProject/blob/ed08945d27613f7d2942baf3e482465483e338bb/web/index.html#L1-L14) |
| dépendances npm | [`package.json`](https://github.com/AshDv/ScribeProject/blob/ed08945d27613f7d2942baf3e482465483e338bb/web/package.json#L1-L19) |
| montage React | [`main.jsx`](https://github.com/AshDv/ScribeProject/blob/ed08945d27613f7d2942baf3e482465483e338bb/web/src/main.jsx#L1-L10) |
| proxy Vite | [`vite.config.js`](https://github.com/AshDv/ScribeProject/blob/ed08945d27613f7d2942baf3e482465483e338bb/web/vite.config.js#L1-L12) |
| première coquille | [`App.jsx` initial](https://github.com/AshDv/ScribeProject/blob/6104ac55c5dad4fe4b6d7382a7ea5d17c9862250/web/src/App.jsx#L1-L7) |
| design initial | [`index.css`](https://github.com/AshDv/ScribeProject/blob/6104ac55c5dad4fe4b6d7382a7ea5d17c9862250/web/src/index.css#L1-L90) |

## Consentement

| Sujet demandé | Lien exact |
|---|---|
| démarrage autorisé | [`start_session`](https://github.com/AshDv/ScribeProject/blob/9040eef62c6f24454db4448c3d2e1b8d197c9010/server/app/consent_routes.py#L165-L184) |
| arrêt manuel | [`stop_session`](https://github.com/AshDv/ScribeProject/blob/9040eef62c6f24454db4448c3d2e1b8d197c9010/server/app/consent_routes.py#L186-L198) |
| vérification du token | [`public_consent`](https://github.com/AshDv/ScribeProject/blob/9040eef62c6f24454db4448c3d2e1b8d197c9010/server/app/consent_routes.py#L200-L207) |
| notice publique | [`get_public_consent`](https://github.com/AshDv/ScribeProject/blob/9040eef62c6f24454db4448c3d2e1b8d197c9010/server/app/consent_routes.py#L209-L223) |
| acceptation | [`accept_consent`](https://github.com/AshDv/ScribeProject/blob/9040eef62c6f24454db4448c3d2e1b8d197c9010/server/app/consent_routes.py#L225-L236) |
| retrait | [`withdraw_consent`](https://github.com/AshDv/ScribeProject/blob/9040eef62c6f24454db4448c3d2e1b8d197c9010/server/app/consent_routes.py#L238-L250) |
| effacement public | [`erase_consent_data`](https://github.com/AshDv/ScribeProject/blob/9040eef62c6f24454db4448c3d2e1b8d197c9010/server/app/consent_routes.py#L252-L280) |
| interface publique | [`PublicConsent`](https://github.com/AshDv/ScribeProject/blob/9040eef62c6f24454db4448c3d2e1b8d197c9010/web/src/PrivacyFlows.jsx#L1-L52) |
| passage légal | [`LegalGate`](https://github.com/AshDv/ScribeProject/blob/9040eef62c6f24454db4448c3d2e1b8d197c9010/web/src/PrivacyFlows.jsx#L58-L94) |

## Dictaphone et upload

| Sujet demandé | Lien exact |
|---|---|
| autorisation d’un enregistrement | [`create_recording`](https://github.com/AshDv/ScribeProject/blob/9040eef62c6f24454db4448c3d2e1b8d197c9010/server/app/routes.py#L211-L262) |
| liste privée | [`list_recordings`](https://github.com/AshDv/ScribeProject/blob/9040eef62c6f24454db4448c3d2e1b8d197c9010/server/app/routes.py#L265-L273) |
| détail privé | [`get_recording`](https://github.com/AshDv/ScribeProject/blob/9040eef62c6f24454db4448c3d2e1b8d197c9010/server/app/routes.py#L276-L282) |
| suppression | [`delete_recording`](https://github.com/AshDv/ScribeProject/blob/9040eef62c6f24454db4448c3d2e1b8d197c9010/server/app/routes.py#L285-L306) |
| parcours réunion | [`MeetingWorkflow`](https://github.com/AshDv/ScribeProject/blob/9040eef62c6f24454db4448c3d2e1b8d197c9010/web/src/MeetingWorkflow.jsx#L1-L15) |
| préparation | [`MeetingSetup`](https://github.com/AshDv/ScribeProject/blob/9040eef62c6f24454db4448c3d2e1b8d197c9010/web/src/MeetingWorkflow.jsx#L17-L59) |
| suivi des accords | [`ConsentStatus`](https://github.com/AshDv/ScribeProject/blob/9040eef62c6f24454db4448c3d2e1b8d197c9010/web/src/MeetingWorkflow.jsx#L61-L95) |
| dictaphone complet | [`Recorder`](https://github.com/AshDv/ScribeProject/blob/9040eef62c6f24454db4448c3d2e1b8d197c9010/web/src/MeetingWorkflow.jsx#L97-L217) |
| multipart frontend | [`createRecording` dans api.js](https://github.com/AshDv/ScribeProject/blob/9040eef62c6f24454db4448c3d2e1b8d197c9010/web/src/api.js#L75-L87) |

## IA

| Sujet demandé | Lien exact |
|---|---|
| schéma des locuteurs | [`Speaker`](https://github.com/AshDv/ScribeProject/blob/9040eef62c6f24454db4448c3d2e1b8d197c9010/server/app/llm.py#L16-L20) |
| schéma des actions | [`ActionItem`](https://github.com/AshDv/ScribeProject/blob/9040eef62c6f24454db4448c3d2e1b8d197c9010/server/app/llm.py#L36-L42) |
| couverture | [`Coverage`](https://github.com/AshDv/ScribeProject/blob/9040eef62c6f24454db4448c3d2e1b8d197c9010/server/app/llm.py#L57-L69) |
| objet racine | [`MeetingSummary`](https://github.com/AshDv/ScribeProject/blob/9040eef62c6f24454db4448c3d2e1b8d197c9010/server/app/llm.py#L72-L82) |
| prompt système | [`SYSTEM_PROMPT`](https://github.com/AshDv/ScribeProject/blob/9040eef62c6f24454db4448c3d2e1b8d197c9010/server/app/llm.py#L85-L101) |
| appel Mistral | [`generate_summary`](https://github.com/AshDv/ScribeProject/blob/9040eef62c6f24454db4448c3d2e1b8d197c9010/server/app/llm.py#L104-L166) |
| pipeline complet | [`process_recording`](https://github.com/AshDv/ScribeProject/blob/9040eef62c6f24454db4448c3d2e1b8d197c9010/server/app/processing.py#L24-L120) |

# 32. Ce qui est à Yanis et ce qui ne l’est pas

## Yanis peut dire « j’ai réalisé »

- configuration et outillage initial ;
- connexion SQLModel et cycle FastAPI initial ;
- fondation React/Vite et design initial ;
- démarrage, arrêt, acceptation, retrait et effacement par lien ;
- interface publique de consentement ;
- contrôle serveur et stockage temporaire de l’upload ;
- dictaphone et machine à états navigateur ;
- schémas Pydantic du rapport ;
- prompt et appel direct Mistral ;
- orchestration transcription-résumé-persistance-nettoyage.

## Yanis doit dire « j’ai intégré/utilisé »

- `User`, `Recording`, `ParticipantConsent`, `StructuredReport` : modèles principalement écrits par
  Ashwin ;
- `transcribe_audio` : client Voxtral écrit par Ashwin ;
- authentification et JWT : Aymen ;
- création initiale des invitations et SMTP : Mehdi ;
- notices légales initiales : Mehdi ;
- tests d’intégration finaux : Aymen ;
- écran final global et intégration graphique : contributions d’équipe.

Comprendre une dépendance ne signifie pas revendiquer son commit.

# 33. Questions exactes du professeur : réponses prêtes

## « Qu’est-ce qu’un harness IA ? »

Un harness IA est l’environnement d’exécution d’un agent de développement. Il lui fournit l’accès
au dépôt, au terminal, aux fichiers et aux tests. Codex ou Claude Code sont des exemples. Le harness
n’est pas une preuve de qualité : la compréhension, la revue, les tests et l’historique restent
nécessaires.

## « C’est quoi un Dockerfile ? »

Un Dockerfile décrit les étapes de construction d’une image de conteneur : image de base, fichiers,
dépendances et commande de démarrage. Les dix commits de Yanis n’en contiennent pas. Le MVP local
utilise `start.ps1`; il n’est donc pas conteneurisé dans cette version.

## « Le dollar, c’est quoi ? »

Dans PowerShell, `$nom` désigne une variable. Dans une chaîne JavaScript entre accents graves,
`${expression}` insère le résultat d’une expression.

## « TypeScript, c’est quoi ? »

TypeScript est JavaScript avec un système de types vérifié avant exécution. Il est transformé en
JavaScript. Scribe utilise JavaScript/JSX, pas TypeScript.

## « Différence TypeScript et JavaScript ? »

JavaScript est exécuté par le navigateur. TypeScript ajoute des annotations, interfaces et contrôles
statiques, puis produit du JavaScript. TypeScript réduit certaines erreurs mais ajoute un outillage
et des types à maintenir.

## « JavaScript vanilla, c’est quoi ? »

JavaScript sans bibliothèque ou framework. Scribe utilise React pour l’UI, mais ses appels `fetch`,
`MediaRecorder`, `Blob` et `getUserMedia` utilisent des API vanilla du navigateur.

## « React, c’est quoi ? »

Une bibliothèque JavaScript pour construire des interfaces par composants et état. Ce n’est ni un
langage ni une base de données.

## « Vite, c’est quoi ? »

Un outil de développement et de build frontend. Il sert le code, transforme JSX, recharge rapidement
et construit les fichiers optimisés. Il ne remplace ni React ni Node.

## « Node.js, c’est quoi ? »

Un environnement qui exécute JavaScript hors navigateur. Vite et npm tournent avec Node pendant le
développement. L’interface finale s’exécute dans le navigateur.

## « npm, c’est quoi ? »

Le gestionnaire de paquets de l’écosystème Node. Il lit `package.json`, télécharge les dépendances et
utilise `package-lock.json` pour les versions exactes.

## « PEP 8, c’est quoi ? »

Le guide de style Python : indentation, nommage, imports, espaces et lisibilité. Le projet le fait
appliquer en partie par Ruff avec une longueur d’équipe de 100 caractères.

## « Python 3.12, les chiffres signifient quoi ? »

3 est la version majeure, 12 la version mineure, et un éventuel troisième nombre est le correctif.
Python 3.12 n’est pas une « version majeure 12 ».

## « Une annotation Python, c’est quoi ? »

Une indication de type comme `recording_id: str` ou `-> None`. Elle documente et aide les outils.
Pydantic peut l’utiliser pour valider, mais Python ne l’impose pas automatiquement partout.

## « Une fonction, c’est quoi ? »

Un bloc nommé réutilisable recevant éventuellement des paramètres et renvoyant éventuellement une
valeur. Exemple : `generate_summary` reçoit transcription et segments, puis renvoie un
`MeetingSummary`.

## « Une variable, c’est quoi ? »

Un nom associé à une valeur. `path` référence un objet chemin ; `seconds` référence le compteur
React courant.

## « Un dictionnaire, c’est quoi ? »

Une collection Python clé-valeur. Le `payload` associe `participants`, `full_transcript` et
`diarized_segments` à leurs valeurs.

## « Une classe, c’est quoi ? »

Un modèle définissant un type d’objet. `ActionItem` décrit les champs valides d’une action.

## « Un constructeur, c’est quoi ? »

Le mécanisme d’initialisation d’une instance. `Recording(...)` construit un objet Recording à partir
d’arguments nommés.

## « Une instance, c’est quoi ? »

Un objet concret créé à partir d’une classe. `settings` est une instance de `Settings` ;
`recording` est une instance de `Recording`.

## « Héritage, c’est quoi ? »

Une classe reprend les comportements d’une classe parente. `MeetingSummary(BaseModel)` hérite des
capacités de validation Pydantic.

## « API REST, c’est quoi ? »

Une API HTTP organisée autour de ressources et verbes. Scribe crée, liste, lit et supprime les
enregistrements avec POST, GET et DELETE.

## « Différence API et SDK ? »

L’API est le contrat de communication. Le SDK est une boîte à outils cliente qui facilite son
utilisation. Yanis appelle l’API Mistral directement avec `httpx`, sans SDK Mistral.

## « Quels types d’API connais-tu ? »

REST, GraphQL, SOAP, gRPC, WebSocket, webhooks et API natives de langage/navigateur. Elles répondent
à des besoins différents.

## « Une clé API, c’est quoi ? »

Un secret qui identifie le compte appelant auprès d’un service, autorise des opérations et rattache
quota/facturation. Elle reste côté backend et doit être révoquée si exposée.

## « SQL et NoSQL, différence ? »

SQL relationnel utilise tables, relations et contraintes. NoSQL couvre documents, clé-valeur,
graphes et autres modèles. Scribe utilise SQLite relationnelle.

## « ORM, c’est quoi ? »

Object-Relational Mapping : conversion entre objets Python et lignes SQL. SQLModel permet
`session.get(Recording, id)` au lieu d’écrire chaque requête brute.

## « Une table, c’est quoi ? »

Une structure relationnelle composée de colonnes et de lignes. Yanis insère notamment des lignes
`Recording`, `SessionRecording` et `StructuredReport`.

## « Une clé primaire, c’est quoi ? »

L’identifiant unique d’une ligne. `recording.id` permet de retrouver un enregistrement.

## « Une clé étrangère, c’est quoi ? »

Une colonne reliant une ligne à une autre table. `SessionRecording.recording_id` relie la réunion à
l’enregistrement.

## « SHA-256, c’est quoi ? »

Une fonction de hash cryptographique produisant 256 bits. Yanis l’utilise pour ne pas stocker le
token public en clair. Ce n’est pas le hash des mots de passe, qui utilise bcrypt.

## « Hash et chiffrement, différence ? »

Le chiffrement est réversible avec une clé. Un hash vise une empreinte non réversible. On compare
des empreintes au lieu de retrouver l’entrée.

## « Pourquoi HTTPS ? »

Pour chiffrer le trafic réseau et authentifier le serveur. Sans HTTPS, audio, tokens et clés de
session peuvent être interceptés.

## « Qu’est-ce que CORS ? »

Une politique appliquée par les navigateurs pour la lecture de réponses entre origines. Ce n’est ni
une authentification ni un pare-feu serveur.

## « Qu’est-ce qu’un middleware ? »

Une couche qui traite la requête/réponse autour des routes. Scribe utilise les middlewares de session
et CORS.

## « ASGI et Uvicorn ? »

ASGI est l’interface Python asynchrone entre serveur et application. Uvicorn est le serveur qui
charge l’objet FastAPI.

## « Pourquoi FastAPI ? »

API rapide à écrire, annotations, validation Pydantic, injection de dépendances, documentation
OpenAPI. Limite : cela ne fournit pas automatiquement une architecture de production.

## « Pourquoi SQLite ? »

Zéro serveur, simple et suffisant pour une démonstration locale. Limite : fichier local, concurrence
et multi-instance. PostgreSQL managé serait plus adapté au déploiement.

## « Pourquoi SQLModel ? »

Il combine modèles Pydantic et ORM SQLAlchemy dans une syntaxe compacte. Il reste nécessaire de
comprendre les transactions et SQL.

## « Pourquoi React et pas du HTML seul ? »

Le dictaphone possède plusieurs états, appels et écrans dynamiques. React rend ces transitions
déclaratives. Pour une page statique, React aurait été inutile.

## « Pourquoi Vite ? »

Configuration légère, JSX, rechargement rapide et proxy. Limite constatée : version Node minimale
non vérifiée dans le script.

## « Pourquoi `useRef` et pas une variable ? »

Une variable normale est recréée à chaque rendu. Une ref garde MediaRecorder et le stream sans
provoquer de rendu.

## « Pourquoi `useState` ? »

Parce que la valeur influence l’interface. Quand `state` change, React doit afficher de nouveaux
boutons.

## « Pourquoi `useEffect` ? »

Pour synchroniser avec les timers, le réseau et le micro, puis les nettoyer.

## « Pourquoi nettoyer un intervalle ? »

Sinon il continue après la disparition du composant, provoque appels inutiles et fuites.

## « Qu’est-ce qu’un Blob ? »

Un objet navigateur contenant des données binaires et un type MIME. Ici, il contient l’audio avant
l’upload.

## « Qu’est-ce qu’un type MIME ? »

Une étiquette du format, comme `audio/webm`. Elle aide au traitement mais peut être falsifiée par le
client.

## « Pourquoi FormData ? »

Pour transmettre champs texte et fichier binaire en multipart sans encoder l’audio en base64.

## « Pourquoi 202 ? »

Le serveur accepte l’upload, mais le traitement IA se termine plus tard.

## « BackgroundTasks, c’est une file ? »

Non. C’est une tâche dans le processus FastAPI après la réponse. Elle n’est pas durable.

## « Qu’est-ce que la diarisation ? »

Découper la parole en segments attribués à des labels de locuteurs. Ce n’est pas une identification
certaine des personnes.

## « Pourquoi deux modèles IA ? »

Voxtral traite le son ; Mistral structure le texte. Les tâches, coûts et métriques sont différents.

## « Pourquoi le modèle Medium ? »

Pour un compromis qualité/coût sur une sortie structurée complexe. Le choix doit être validé par
benchmark et disponibilité réelle du compte.

## « Pourquoi température zéro ? »

Pour réduire la variation et la créativité. Cela ne garantit pas l’absence d’hallucination.

## « Pourquoi du JSON Schema ? »

Pour imposer champs et types au modèle. Pydantic revérifie ensuite côté serveur.

## « Pourquoi une couverture des segments ? »

Pour détecter un segment oublié ou dupliqué. Cela ne valide pas automatiquement la vérité du résumé.

## « Chaque mot est-il utilisé ? »

Chaque segment doit être classé une fois. Les fillers peuvent être exclus avec justification. Le
contrôle ne prouve pas l’usage littéral de chaque mot.

## « KISS, c’est quoi ? »

Keep It Simple, Stupid : choisir la solution la plus simple qui répond correctement au besoin. Cela
ne signifie ni tout mettre dans un fichier ni supprimer les contrôles.

## « DRY, c’est quoi ? »

Don’t Repeat Yourself : une règle métier doit avoir une source claire. Les helpers
`owned_recording`, `recording_detail` et `act` réduisent la répétition.

## « Moins de lignes veut dire meilleur code ? »

Non. Le CSS compact le montre : moins de lignes physiques peut être moins lisible. L’objectif est
moins de complexité et de duplication, pas un concours de compression.

# 34. Questions agressives spécifiques à la partie Yanis

## Consentement et RGPD

**Le lien de consentement expire-t-il ?**  
Non dans le MVP. Le token est fort et stocké haché, mais il faut ajouter expiration, rotation et
journalisation.

**Si je transfère mon e-mail, l’autre personne peut-elle consentir à ma place ?**  
Oui, le lien agit comme un Bearer token. C’est une limite du mécanisme sans authentification.

**Un participant peut-il effacer le résultat de tous les autres ?**  
La route actuelle supprime tous les enregistrements de la réunion. C’est trop large pour une
production et doit devenir un workflow d’effacement maîtrisé.

**Le retrait arrête-t-il vraiment le micro ?**  
Le serveur change l’état immédiatement ; le navigateur le détecte par polling au plus tôt lors de
la prochaine vérification. En panne réseau, le comportement n’est pas fail-closed.

**Que se passe-t-il si le retrait arrive après l’upload ?**  
Le statut de réunion s’arrête, mais le traitement déjà lancé n’est pas annulé automatiquement par
ce code. Il faut une vérification dans le worker et une politique d’effacement.

**Pourquoi demander aussi une annonce dans la salle ?**  
L’accord préalable par e-mail ne remplace pas l’information au moment réel de la captation.

**Pouvez-vous dire 100 % RGPD ?**  
Non. Le code met en œuvre des mesures, mais contrats, DPA, hébergement, registre, sauvegardes,
procédures et validation juridique restent nécessaires.

## Audio

**Le navigateur garantit-il WebM ?**  
Non. MediaRecorder choisit selon le navigateur. Le code lit son `mimeType`, mais le nom frontend
reste `.webm`. Une négociation de codec manque.

**Le type MIME prouve-t-il le format ?**  
Non. Le client peut mentir.

**Pourquoi lire 50 MiB en mémoire ?**  
Simplicité du MVP. La production doit streamer vers un stockage objet.

**Où est l’audio avant l’envoi ?**  
Dans des chunks puis un Blob en mémoire navigateur, accessible par une URL locale `blob:`.

**Où est-il après l’envoi ?**  
Dans le dossier temporaire configuré jusqu’au bloc de suppression du pipeline.

**Est-il toujours supprimé ?**  
Après un traitement normal ou une erreur capturée, oui. Un crash brutal avant `finally` peut le
laisser.

## IA

**Utilisez-vous le SDK Mistral ?**  
Non, appel REST direct avec HTTPX.

**Le modèle indiqué existe-t-il forcément pour votre clé ?**  
Non. Le nom est configurable ; la disponibilité doit être testée sur le compte.

**`safe_prompt` garantit-il la sécurité ?**  
Non. C’est un paramètre fournisseur, pas une garantie globale.

**La transcription peut-elle injecter des instructions ?**  
Oui, c’est une donnée non fiable. Le message système et le JSON réduisent le risque, sans le
supprimer.

**Les e-mails sont-ils vraiment absents de Mistral ?**  
Les listes d’e-mails ne sont pas envoyées au résumé. Mais un e-mail prononcé peut apparaître dans la
transcription. Une redaction explicite manque.

**Pourquoi deux stockages du rapport ?**  
Champs rapides dans `Recording` et détail dans `StructuredReport`. Cela simplifie la lecture mais
duplique des données.

**Le contrôle de couverture valide-t-il les décisions ?**  
Non. Il valide les IDs couverts, pas la justesse sémantique.

## Architecture

**Est-ce réellement serverless ?**  
Pas dans la version locale : SQLite, disque et tâche en processus. La cible doit utiliser base
managée, stockage objet et file/worker managé.

**Que se passe-t-il si FastAPI redémarre pendant le résumé ?**  
La tâche peut être perdue et le statut rester `PROCESSING`.

**Deux workers peuvent-ils traiter le même audio ?**  
Oui en cas de course. La garde actuelle n’est pas une acquisition atomique.

**Pourquoi pas Docker ?**  
Le sprint a privilégié le lancement local. Un Dockerfile n’a pas été intégré dans les commits
étudiés.

# 35. Audit technique maximal : défauts classés

## Priorité critique avant production

1. L’effacement public peut supprimer toute la réunion.
2. Les tokens publics n’expirent pas.
3. Le retrait dépend d’un polling qui ignore les pannes réseau.
4. `BackgroundTasks` n’est pas durable.
5. SQLite et disque local ne conviennent pas au serverless multi-instance.
6. Une course peut lancer deux traitements.
7. Une suppression de fichier peut précéder un commit SQL qui échoue.

## Priorité élevée

1. MIME déclaré non vérifié par contenu.
2. Fichier complet chargé en mémoire.
3. Absence de retry idempotent et de file.
4. Paramètres exacts du modèle à vérifier.
5. E-mail éventuellement présent dans une transcription envoyée au sous-traitant.
6. Contrôle de couverture limité aux IDs.
7. `IndexError` possible dans l’extraction Mistral.
8. Pas d’expiration ou de révocation des liens de consentement.
9. Pas d’audit robuste des actions sensibles.

## Priorité moyenne

1. JSON stocké dans du texte.
2. Date d’action non typée.
3. `segment_ids` potentiellement vides.
4. `key={index}` sur les participants.
5. erreurs de polling silencieuses.
6. durée UI fondée sur `setInterval`.
7. codecs non négociés.
8. Google Fonts externe.
9. CSS trop compact.
10. styles de fonctionnalités futures dans le commit shell.
11. `CONSENT_VERSION` séparée des versions configurées.
12. nom `original_filename` trompeur.
13. health check superficiel.
14. aucune migration Alembic.
15. aucune vérification de Node dans le script.

## Réponse modèle face à un défaut

> Oui, cette limite existe dans le MVP. Le comportement actuel est exactement X. Le risque est Y.
> Pour la production, je le corrige par Z et j’ajoute le test correspondant.

Ne jamais répondre :

> Ce n’est pas grave.

# 36. Tests que Yanis devrait proposer pour sa partie

Même si les tests finaux ont été écrits par Aymen, Yanis doit savoir proposer ceux de ses fonctions.

## Consentement

- token correct/invalide ;
- token expiré après ajout de l’expiration ;
- acceptation ;
- double acceptation ;
- retrait ;
- retrait pendant enregistrement ;
- arrêt navigateur ;
- échec réseau de polling ;
- effacement sans toucher aux autres participants ;
- traversée de chemin impossible.

## Upload

- sans JWT ;
- mauvais propriétaire ;
- réunion non démarrée ;
- aucun participant ;
- retrait présent ;
- MIME refusé ;
- faux MIME ;
- fichier vide ;
- limite exacte ;
- un octet au-dessus ;
- nom malveillant ;
- suppression d’un autre utilisateur.

## Dictaphone

- permission refusée ;
- démarrage ;
- pause/reprise ;
- stop ;
- reset ;
- retrait ;
- URL Blob révoquée ;
- tracks arrêtées au démontage ;
- échec upload puis retry ;
- navigateur sans MediaRecorder.

## LLM

- clé absente ;
- erreur réseau ;
- 401 fournisseur ;
- réponse sans `choices` ;
- liste vide ;
- JSON invalide ;
- champ manquant ;
- priorité invalide ;
- segment oublié ;
- segment dupliqué ;
- ID inventé dans une action ;
- instruction malveillante dans la transcription.

## Pipeline

- enregistrement absent ;
- déjà en traitement ;
- deux appels concurrents ;
- lien absent ;
- transcription échoue ;
- résumé échoue ;
- sauvegarde réussie ;
- audio supprimé ;
- erreur de suppression ;
- commit échoue ;
- retry après crash.

# 37. Exercices de soutenance

## Exercice 1 — une ligne Python

Le professeur montre :

```python
recording.segments_json = json.dumps(transcript["segments"], ensure_ascii=False)
```

Réponse :

> `recording` est une instance SQLModel. `segments_json` est un champ texte. Je prends la liste des
> segments dans le dictionnaire de transcription, puis `json.dumps` la sérialise en chaîne JSON.
> `ensure_ascii=False` conserve les accents. Ce choix est KISS pour SQLite, mais JSONB ou des tables
> normalisées faciliteraient les recherches.

## Exercice 2 — une ligne React

```javascript
const recorder = useRef(null);
```

Réponse :

> `const` crée un nom non réassigné. `useRef` crée un objet stable avec `.current`, initialement
> `null`. J’y place le MediaRecorder, car il doit survivre aux rendus sans provoquer un rendu à
> chaque changement.

## Exercice 3 — une route

```python
@router.post("/recordings", status_code=202)
```

Réponse :

> C’est un décorateur FastAPI. Il relie la fonction suivante à un POST. La route accepte un nouvel
> enregistrement et renvoie 202, car le traitement IA est lancé après la réponse.

## Exercice 4 — une annotation

```python
participant_names: list[str]
```

Réponse :

> C’est une annotation Python : une liste de chaînes. Elle documente, aide l’IDE et peut être
> exploitée par des outils, mais une fonction Python ordinaire ne la valide pas automatiquement.

## Exercice 5 — une règle CSS

```css
.orb.live { animation:pulse 1.8s ease-in-out infinite; }
```

Réponse :

> Le sélecteur exige les classes `orb` et `live`. La classe `live` n’est ajoutée que pendant
> l’enregistrement. L’animation `pulse` dure 1,8 seconde, accélère et ralentit, puis se répète.

## Exercice 6 — une requête ORM

```python
select(Recording).where(Recording.owner_id == user.id)
```

Réponse :

> SQLModel construit une requête SQL paramétrée sur la table Recording. Le filtre impose le
> propriétaire authentifié. L’ORM produit ensuite des instances Python.

## Exercice 7 — un contrôle IA

```python
if set(covered) != expected or len(covered) != len(expected):
```

Réponse :

> Le set compare les IDs sans ordre. La longueur détecte les doublons. Cela garantit une entrée de
> couverture par segment attendu, mais pas la vérité du contenu.

# 38. Chiffres du code personnel à connaître

Les dix commits fonctionnels de Yanis ajoutent environ :

- 3 102 lignes selon Git ;
- dont 1 802 lignes de `package-lock.json` générées ;
- environ 1 300 autres ajouts, incluant code, configuration, CSS, commentaires et certaines lignes
  de reformatage.

Fichiers importants :

- `config.py` : 74 lignes ;
- `db.py` : 22 lignes ;
- `main.py` initial : 38 lignes ;
- `MeetingWorkflow.jsx` au commit : 217 lignes ;
- fonction `Recorder` : environ 121 lignes dans ce commit ;
- `llm.py` : 166 lignes ;
- `processing.py` final : 120 lignes ;
- CSS initial : 90 lignes physiques très compactes.

Ne jamais confondre nombre de lignes et valeur. Le lockfile est généré ; le CSS contient plusieurs
déclarations par ligne.

# 39. Réponse à « pourquoi avoir choisi cette architecture ? »

## Pour le sprint

> Nous avions quatre jours pour montrer un parcours complet. Nous avons choisi des technologies
> simples et compatibles : React/Vite dans le navigateur, FastAPI/Pydantic au backend, SQLModel avec
> SQLite localement, puis les API Mistral. Les API natives du navigateur évitent une dépendance de
> dictaphone supplémentaire.

## Pour la qualité

> Les règles sensibles sont au backend. Le frontend guide l’utilisateur, mais l’API revérifie le
> propriétaire, l’état de réunion, tous les accords, le format et la taille.

## Pour l’IA

> Nous séparons STT et synthèse. La transcription produit des segments, puis un schéma strict impose
> un rapport traçable. Le serveur valide avant d’enregistrer.

## Pour la confidentialité

> L’audio est temporaire, les liens sont hachés en base et le retrait arrête l’état serveur. Je
> reconnais que le mécanisme d’effacement et le déclenchement temps réel doivent encore être durcis.

## Pour la production

> Je ne conserverais pas SQLite, le disque local ni BackgroundTasks. La cible serait frontend
> statique, API serverless, PostgreSQL managé, stockage objet chiffré, file de tâches et worker
> idempotent.

# 40. Pitch Yanis de cinq minutes

> Ma contribution commence par la fondation technique. Dans `config.py`, j’ai centralisé les
> variables d’environnement avec Pydantic Settings. Les valeurs sont typées et le vrai `.env` est
> ignoré par Git. J’ai posé SQLModel avec une session par requête, le cycle de vie FastAPI, les
> middlewares et un health check. Pour le frontend, j’ai installé React et Vite, configuré le proxy
> vers l’API et créé le design initial responsive.
>
> J’ai ensuite développé la partie consentement révocable. Un lien contient un token aléatoire, mais
> la base n’en stocke que le SHA-256. Le démarrage exige l’annonce dans la salle et l’accord actif de
> tous les participants. Le retrait change immédiatement l’état serveur à STOPPED. Le navigateur
> vérifie cet état toutes les trois secondes et détruit le Blob local s’il détecte un retrait.
>
> Le dictaphone utilise les API natives `getUserMedia` et `MediaRecorder`. Je conserve l’objet
> recorder, le stream et les chunks dans des refs React. Les états `idle`, `recording`, `paused`,
> `ready` et `uploading` déterminent l’interface. À l’arrêt, les chunks deviennent un Blob et une URL
> locale. L’upload utilise FormData. Côté serveur, je revérifie tous les consentements, le propriétaire,
> le MIME et la taille, puis j’enregistre temporairement sous un UUID.
>
> Pour le compte rendu, j’ai créé des modèles Pydantic : locuteurs, décisions, actions, questions,
> risques et couverture. Le prompt interdit d’inventer, demande les IDs sources et exige une entrée
> de couverture par segment. J’appelle directement l’API Mistral avec HTTPX et un JSON Schema strict,
> puis Pydantic valide la réponse. Une vérification supplémentaire compare les IDs couverts.
>
> Enfin, `process_recording` ouvre sa propre session, passe l’état à PROCESSING, appelle la
> transcription Voxtral créée par Ashwin, puis mon résumé Mistral. Les résultats rapides sont stockés
> dans Recording et les détails dans StructuredReport. Le bloc `finally` supprime l’audio et arrête
> la réunion.
>
> Je distingue clairement le MVP de la production. Les limites principales sont le token public
> sans expiration, un effacement trop large, le polling silencieux en panne réseau, le MIME déclaré,
> SQLite, le disque local et BackgroundTasks non durable. Ma cible est une base managée, un stockage
> objet, une file et un worker idempotent.

# 41. Fiche ultime à réciter la veille

## Stack

```text
Frontend : HTML, CSS, JavaScript/JSX, React 18, Vite
Backend : Python, FastAPI, Pydantic, SQLModel, SQLite local
Audio : getUserMedia, MediaRecorder, Blob, multipart
IA : Voxtral STT + diarisation, Mistral résumé, JSON Schema
Outillage : Git, GitHub, npm, pip, Ruff, Pytest, PowerShell
```

## Mes dix commits

```text
1 configuration
2 base + FastAPI
3 React + Vite
4 design initial
5 acceptation/retrait/effacement
6 page publique
7 upload sécurisé
8 dictaphone
9 rapport structuré
10 pipeline
```

## Mes notions incontournables

```text
variable, fonction, paramètre, argument, retour
classe, objet, instance, constructeur
liste, dictionnaire, tuple, set
annotation, exception, context manager
JSX, composant, prop, state, ref, effect
HTML sémantique, CSS cascade, flex, grid, responsive
HTTP, REST, JSON, multipart, MIME, CORS
SQL, table, clé, ORM, transaction
STT, LLM, token, prompt, hallucination, diarisation
API, SDK, clé API, JSON Schema
Git, branche, commit, PR, Conventional Commits
```

## Mes limites à annoncer avant qu’on me piège

```text
pas encore serverless en production
SQLite et disque uniquement pour le MVP local
BackgroundTasks non durable
polling toutes les trois secondes
échec réseau de polling ignoré
token public sans expiration
effacement public trop large
MIME non vérifié dans les octets
fichier chargé en mémoire
modèle et paramètres à confirmer sur le compte
couverture segmentaire, pas preuve de vérité
audio supprimable après flux normal, pas garanti après crash brutal
```

## Ma règle de réponse

```text
Je montre le fichier.
Je nomme la syntaxe.
J’explique l’entrée.
J’explique la sortie.
Je justifie le choix.
Je reconnais la limite.
Je propose la correction et le test.
```

---

# 42. Localhost, réseau et ports — explication complète

## Réponse directe à « si quelqu’un a mon lien localhost, a-t-il accès ? »

Pour le lien :

```text
http://localhost:5174/
```

la réponse normale est **non depuis un autre ordinateur**.

`localhost` signifie toujours :

```text
cet ordinateur lui-même
```

Si Yanis ouvre le lien sur son PC, il contacte le PC de Yanis.  
Si Aymen ouvre exactement le même lien sur son PC, il contacte le PC d’Aymen.  
Si aucun serveur ne tourne chez Aymen sur le port 5174, il obtient une page inaccessible.

Le texte `localhost` ne contient pas l’adresse de la machine de Yanis.

### Tableau des scénarios

| Personne et situation | Accès avec `http://localhost:5174` |
|---|---|
| Yanis, serveur lancé sur son PC | oui |
| autre utilisateur connecté sur le même PC | probablement oui |
| programme malveillant exécuté sur le même PC | peut tenter l’accès |
| Aymen sur son propre PC | non, il vise son propre PC |
| personne sur le même Wi-Fi | non avec ce lien seul |
| personne sur Internet | non avec ce lien seul |
| personne ayant un tunnel public vers le PC | éventuellement oui via l’URL du tunnel |
| personne utilisant l’IP LAN après exposition du serveur | éventuellement oui |

Important :

> `localhost` empêche normalement l’accès réseau extérieur, mais ce n’est pas un mot de passe. Tout
> programme autorisé à tourner sur la même machine peut essayer de contacter le service.

### Voir l’application ne signifie pas accéder à toutes les données

Il faut distinguer trois niveaux :

1. **atteindre le port** : une connexion réseau arrive au serveur ;
2. **charger le frontend** : les fichiers HTML/JS/CSS sont visibles ;
3. **utiliser une route privée** : un JWT valide et la bonne autorisation sont nécessaires.

Une personne sur le même PC peut normalement charger la page si Vite tourne. Elle ne peut pas pour
autant lire les enregistrements d’un compte sans son Bearer token.

Certaines routes restent volontairement publiques :

- `/api/health` ;
- consultation et action de consentement avec le token du lien.

Pour ces routes, le token du lien est l’autorisation. S’il fuit, la protection est compromise même
si aucun mot de passe utilisateur n’a été donné.

## Adresse de boucle locale

`localhost` est un nom généralement résolu vers :

```text
127.0.0.1   en IPv4
::1         en IPv6
```

Ces adresses appartiennent à l’interface de boucle locale ou loopback. Les paquets restent dans le
système d’exploitation ; ils ne partent pas vers le routeur.

Les trois écritures suivantes peuvent viser le même ordinateur :

```text
http://localhost:5174
http://127.0.0.1:5174
http://[::1]:5174
```

Selon la configuration, un serveur peut écouter seulement IPv4, seulement IPv6 ou les deux.

## Décomposition complète d’une URL

```text
http://localhost:5174/api/health?details=true#result
```

| Partie | Valeur | Rôle |
|---|---|---|
| schéma | `http` | protocole applicatif |
| hôte | `localhost` | machine ciblée |
| port | `5174` | programme ciblé sur la machine |
| chemin | `/api/health` | ressource demandée |
| query string | `?details=true` | paramètres de requête |
| fragment | `#result` | navigation traitée côté navigateur |

Le fragment n’est normalement pas envoyé au serveur HTTP. La query string et le chemin le sont.

## Qu’est-ce qu’un port ?

Une adresse IP identifie une interface réseau sur une machine. Le port permet de choisir le
programme ou service sur cette machine.

Analogie :

```text
adresse IP = adresse de l’immeuble
port       = numéro d’appartement
```

Un port est un entier entre 0 et 65 535. Une même machine peut donc exposer plusieurs services :

```text
localhost:5174  -> Vite / frontend
localhost:8000  -> Uvicorn / FastAPI
smtp.example:587 -> soumission d’e-mail
```

Le port fait partie de la connexion réseau. Pour HTTP, le transport est généralement TCP.

## Port par défaut

Lorsque le port n’apparaît pas :

- HTTP utilise normalement 80 ;
- HTTPS utilise normalement 443.

Ces URL sont donc équivalentes dans leur intention :

```text
http://example.com
http://example.com:80
```

Le projet local utilise des ports non standards pour faire tourner plusieurs serveurs sans droits
administrateur particuliers.

## Socket

Une socket est une extrémité de communication identifiée notamment par :

- protocole ;
- adresse IP ;
- port.

Une connexion TCP possède une extrémité cliente et une extrémité serveur.

Le navigateur choisit généralement un port client temporaire, puis contacte :

```text
127.0.0.1:5174
```

## Processus

Un processus est un programme en cours d’exécution.

Dans la démonstration :

- un processus Node exécute Vite ;
- un processus Python/Uvicorn exécute FastAPI ;
- le navigateur est un autre processus ;
- SQLite est un fichier utilisé par le processus backend, pas un serveur séparé.

Si Vite s’arrête, le port 5174 ne répond plus.  
Si FastAPI s’arrête, l’interface peut encore s’afficher, mais les appels `/api` échouent.

## « Le port est déjà utilisé »

Deux processus ne peuvent généralement pas écouter la même combinaison adresse/port en même temps.

Exemple :

```text
Address already in use
```

Cela signifie souvent :

- ancien serveur encore lancé ;
- autre application sur 5174 ou 8000 ;
- double lancement du script.

Dans Vite :

```javascript
strictPort: true
```

demande d’échouer plutôt que de choisir automatiquement 5175. Cela évite de casser les URLs,
callbacks et règles CORS.

## Adresse d’écoute ou bind

Un serveur ne se contente pas de choisir un port. Il choisit aussi l’adresse sur laquelle écouter.

### `127.0.0.1`

Écoute seulement sur la boucle locale :

```text
accessible depuis la machine
inaccessible directement depuis le réseau local
```

### `0.0.0.0`

Demande d’écouter sur toutes les interfaces IPv4 disponibles :

```text
loopback
Wi-Fi
Ethernet
autres interfaces
```

`0.0.0.0` est une adresse d’écoute, pas normalement l’adresse que l’on envoie à un collègue. Le
collègue utilise l’adresse réelle de la machine, par exemple :

```text
http://192.168.1.42:5174
```

### Configuration actuelle de Scribe

Le script lance Uvicorn sans `--host` :

```powershell
python.exe -m uvicorn app.main:app --reload --port 8000
```

Uvicorn écoute donc normalement sur `127.0.0.1`.

Vite est lancé sans option `--host`, et sa configuration ne définit que le port. Il reste donc
normalement local.

La version actuelle n’est pas volontairement exposée au Wi-Fi ou à Internet.

## IP privée et réseau local

Un PC connecté à une box reçoit souvent une adresse privée ressemblant à :

```text
192.168.x.x
10.x.x.x
172.16.x.x à 172.31.x.x
```

Ces adresses sont utilisables dans le réseau local, pas directement routées sur tout Internet.

Pour partager sur le même Wi-Fi, il faudrait au minimum :

1. faire écouter les serveurs sur les interfaces réseau ;
2. utiliser l’IP privée du PC ;
3. autoriser les ports dans le pare-feu ;
4. configurer les URLs frontend/backend ;
5. configurer CORS ;
6. vérifier les règles du microphone ;
7. protéger les secrets et données ;
8. arrêter l’exposition après le test.

Ce n’est pas recommandé comme hébergement final.

## IP publique et NAT

La box possède généralement une adresse IP publique et utilise le NAT pour partager la connexion
entre les appareils privés.

Un ordinateur extérieur ne peut normalement pas initier une connexion vers le PC de Yanis sans :

- redirection de port sur le routeur ;
- tunnel ;
- VPN ;
- service d’hébergement ;
- autre règle réseau explicite.

Ouvrir une redirection de port vers un serveur de développement est risqué :

- Uvicorn tourne avec `--reload` ;
- Vite est un serveur de développement ;
- aucune protection de production ;
- logs et erreurs peuvent être détaillés ;
- la machine personnelle devient exposée.

## Pare-feu

Le pare-feu autorise ou refuse le trafic entrant et sortant selon :

- programme ;
- port ;
- protocole ;
- profil réseau ;
- adresse source.

Même si un serveur écoute sur `0.0.0.0`, le pare-feu Windows peut bloquer les autres machines.

Inversement, autoriser le pare-feu ne suffit pas si le serveur écoute seulement `127.0.0.1`.

## DNS

DNS transforme un nom comme :

```text
app.scribe.fr
```

en adresse IP.

`localhost` est un nom spécial local. Il n’a pas besoin de désigner le PC de Yanis dans un DNS
public.

Un nom de domaine OVH peut pointer vers un service hébergé, mais posséder le nom ne crée ni serveur,
ni backend, ni sécurité.

## Domaine, sous-domaines et environnement

Une architecture de production pourrait utiliser :

```text
app.scribe.fr -> frontend
api.scribe.fr -> backend
```

Si frontend et backend ont des origines différentes, CORS doit autoriser le frontend.

Une autre solution :

```text
scribe.fr/api -> reverse proxy -> backend
scribe.fr/    -> frontend
```

Le navigateur voit alors une même origine.

## Origine Web

Une origine est le triplet :

```text
schéma + hôte + port
```

Ces deux URLs ont des origines différentes :

```text
http://localhost:5174
http://localhost:8000
```

Le port suffit à créer une autre origine.

## Fonctionnement exact du proxy Vite

La configuration contient :

```javascript
proxy: { "/api": "http://localhost:8000" }
```

Parcours :

```text
React appelle /api/recordings
        |
        v
navigateur contacte localhost:5174
        |
        v
Vite reconnaît le préfixe /api
        |
        v
Vite transmet à localhost:8000/api/recordings
        |
        v
FastAPI répond
        |
        v
Vite renvoie la réponse au navigateur
```

Le frontend n’appelle donc pas directement le port 8000 en développement.

Avantages :

- URL relative simple ;
- même origine vue par le navigateur ;
- moins de problèmes CORS locaux ;
- aucune URL backend dispersée dans React.

Limite :

> Le proxy Vite n’existe pas dans les fichiers statiques construits. L’hébergement final doit
> recréer ce routage ou configurer une URL d’API.

## CORS et localhost

CORS limite la lecture de réponses par le JavaScript d’une autre origine. Ce n’est pas une
protection suffisante contre tous les appels.

Par exemple, un site malveillant peut parfois déclencher certaines requêtes simples sans pouvoir
lire la réponse. Les routes sensibles doivent donc toujours avoir :

- authentification ;
- autorisation ;
- validation ;
- protection CSRF si cookies ;
- méthodes correctes.

Les endpoints publics de consentement reposent sur le secret du token dans l’URL.

## HTTP et HTTPS

HTTP transmet sans chiffrement. HTTPS ajoute TLS :

- chiffrement ;
- intégrité ;
- authentification du serveur par certificat.

`localhost` bénéficie d’exceptions navigateur pour le développement et est généralement considéré
comme contexte sécurisé pour `getUserMedia`.

Une IP LAN en HTTP comme :

```text
http://192.168.1.42:5174
```

peut ne pas être considérée comme contexte sécurisé. Le microphone peut être refusé selon le
navigateur.

En production, HTTPS est obligatoire.

## Pourquoi un lien de consentement localhost ne marche pas ailleurs

L’e-mail peut contenir :

```text
http://localhost:5174/consent/TOKEN
```

Sur le PC du participant, `localhost` vise son propre PC. Son navigateur ne trouve ni Vite, ni la
base de l’organisateur.

Le token peut être correct, mais l’hôte est faux pour cette personne.

Pour une vraie invitation, `FRONTEND_URL` doit être une adresse accessible par les participants :

```text
https://app.scribe.fr
```

Le backend et la base doivent également être accessibles par ce frontend.

## Si quelqu’un connaît le token, peut-il remplacer localhost ?

Si le service est réellement exposé sous une autre adresse, une personne connaissant le token peut
construire :

```text
https://adresse-accessible/consent/TOKEN
```

Le secret principal du lien est le token, pas le mot `localhost`.

Il faut donc :

- ne pas publier le lien ;
- éviter de le journaliser ;
- ajouter expiration ;
- permettre révocation ;
- limiter les actions destructrices ;
- utiliser HTTPS.

## Tunnel

Un tunnel comme ceux proposés par différents outils crée une URL publique qui transfère vers un port
local.

```text
URL publique -> tunnel -> localhost:5174
```

Avantage :

- démonstration rapide.

Risques :

- exposition involontaire ;
- URL transmise à un tiers ;
- service local de développement ;
- secrets et vraies données ;
- tunnel arrêté ou URL changeante ;
- backend 8000 pas forcément correctement routé.

Un tunnel n’est pas un hébergement de production.

## Reverse proxy

Un reverse proxy reçoit les requêtes publiques et les transmet au bon service :

```text
Internet
   |
   v
reverse proxy HTTPS
   +-- /       -> frontend
   `-- /api    -> FastAPI
```

Il peut gérer :

- certificat TLS ;
- domaine ;
- compression ;
- limites de taille ;
- journaux ;
- routage ;
- rate limiting.

## Load balancer

Un load balancer répartit les requêtes entre plusieurs instances.

Avec plusieurs instances, SQLite et le disque local deviennent un problème :

- chaque instance peut avoir son propre fichier ;
- l’upload peut être sur A ;
- le traitement peut démarrer sur B ;
- B ne trouve pas le fichier.

D’où le besoin de base et stockage partagés.

## Commandes de diagnostic réseau

### Voir ce qui écoute sous Windows

```powershell
Get-NetTCPConnection -State Listen |
  Where-Object LocalPort -In 5174,8000
```

### Tester le frontend

```powershell
Test-NetConnection localhost -Port 5174
```

### Tester le backend

```powershell
Test-NetConnection localhost -Port 8000
Invoke-RestMethod http://localhost:8000/api/health
```

### Trouver l’adresse LAN

```powershell
Get-NetIPAddress -AddressFamily IPv4 |
  Where-Object IPAddress -NotLike "127.*"
```

Afficher une IP ne signifie pas qu’il faut exposer le service.

## Réponse parfaite au professeur

> `localhost` est le nom de boucle locale. Sur chaque machine, il désigne cette machine elle-même,
> généralement 127.0.0.1 ou ::1. Le port choisit le processus : 5174 pour Vite et 8000 pour
> FastAPI. Dans notre configuration actuelle, les serveurs écoutent localement, donc envoyer
> `http://localhost:5174` à quelqu’un ne lui donne pas accès à mon PC ; il cherche un serveur sur
> son propre PC. Pour partager réellement, il faudrait exposer une IP ou un domaine, ouvrir le
> réseau, configurer HTTPS, le pare-feu, CORS et les URLs. Le proxy Vite transmet localement `/api`
> de 5174 vers 8000, mais il n’existe pas automatiquement en production.

# 43. Idempotence — explication complète

## Définition simple

Une opération est idempotente lorsque la répéter plusieurs fois produit le même état final utile
que l’exécuter une seule fois.

Notation conceptuelle :

```text
f(f(x)) = f(x)
```

Ce n’est pas une obligation d’avoir exactement :

- le même code HTTP ;
- le même message ;
- le même temps d’exécution.

L’idée principale concerne l’effet final sur le système.

## Exemples simples

### Idempotent

```text
mettre status = STOPPED
mettre le nom = "Yanis"
supprimer une ressource déjà supprimée
```

Après plusieurs répétitions, la cible reste arrêtée, nommée Yanis ou absente.

### Non idempotent

```text
incrémenter compteur de 1
créer une nouvelle ligne
facturer 10 €
envoyer un nouvel e-mail
générer un nouveau rapport payant
```

Chaque répétition ajoute un effet.

## Méthodes HTTP et idempotence

Selon la sémantique HTTP habituelle :

| Méthode | Sûre ? | Idempotente ? | Explication |
|---|---:|---:|---|
| `GET` | oui | oui | lire ne doit pas modifier le métier |
| `HEAD` | oui | oui | lire seulement les en-têtes |
| `PUT` | non | oui | remplacer par le même état |
| `DELETE` | non | oui | la ressource reste absente |
| `POST` | non | pas garanti | crée ou déclenche souvent un nouvel effet |
| `PATCH` | non | pas garanti | dépend de la modification |

« Sûre » signifie sans modification métier intentionnelle.  
« Idempotente » signifie répétable avec le même état final.

Un `DELETE` peut renvoyer 204 la première fois puis 404 la seconde. L’effet final reste « absent ».

## Idempotence dans Scribe

### `stop_session`

Le statut final reste `STOPPED`, mais :

```python
meeting.stopped_at = utc_now()
```

change à chaque appel. L’opération n’est donc pas strictement idempotente sur toutes les données.

Correction :

```python
if meeting.status != ConsentSessionStatus.STOPPED:
    meeting.status = ConsentSessionStatus.STOPPED
    meeting.stopped_at = utc_now()
```

### `accept_consent`

Chaque appel remplace `consented_at` par une nouvelle date. Ce n’est pas strictement idempotent.

Correction possible : conserver la première date active.

### `withdraw_consent`

Même problème avec `withdrawn_at` et `stopped_at`.

### `delete_recording`

L’effet final est idempotent : la ressource est absente. L’implémentation renvoie toutefois 404 au
deuxième appel.

### `process_recording`

Le traitement n’est pas suffisamment idempotent :

- appel Mistral potentiellement refacturé ;
- nouveau rapport ;
- risque de contrainte unique ;
- suppression audio ;
- statuts.

La simple garde `PROCESSING` n’empêche pas toutes les courses.

## Pourquoi l’idempotence est essentielle

Sur un réseau, le client peut ne pas savoir si le serveur a terminé :

```text
client envoie
serveur exécute
réponse perdue
client réessaie
```

Sans idempotence, le retry peut :

- créer deux comptes rendus ;
- envoyer deux e-mails ;
- facturer deux fois ;
- lancer deux modèles.

## Clé d’idempotence

Le client génère une clé unique pour une opération logique :

```http
Idempotency-Key: 6d5d...
```

Le serveur stocke :

- clé ;
- utilisateur ;
- type d’opération ;
- résultat ou statut.

Si la même clé revient, il ne recommence pas l’effet ; il renvoie le résultat déjà connu.

La clé doit être liée à l’utilisateur et à l’opération, avec une durée de conservation.

## Idempotence du worker

Un worker robuste doit pouvoir recevoir le même message plusieurs fois.

Approche :

1. contrainte unique sur le job ou rapport ;
2. acquisition atomique de l’état ;
3. vérifier si le résultat existe déjà ;
4. ne jamais dupliquer une facturation ;
5. étapes reprenables ;
6. suppression de fichier répétable ;
7. stockage du résultat avant accusé de réception.

## Idempotence et déterminisme

Ce sont deux notions différentes.

### Déterminisme

Même entrée, même sortie.

### Idempotence

Répéter l’opération sur son résultat ne change plus l’état.

Un LLM peut être non déterministe même avec température zéro. Le pipeline peut malgré tout être rendu
idempotent en ne relançant pas le LLM pour la même clé.

## Idempotence et pureté

Une fonction pure :

- dépend seulement de ses arguments ;
- n’a pas d’effet de bord.

Une fonction pure n’est pas automatiquement idempotente.

Exemple :

```text
f(x) = x + 1
```

est pure mais pas idempotente.

## Réponse parfaite au professeur

> L’idempotence signifie que répéter la même opération logique ne produit pas un effet supplémentaire
> incorrect. Elle est importante parce qu’un réseau ou une file peut livrer deux fois. Dans Scribe,
> DELETE a un état final idempotent, mais `process_recording` ne l’est pas encore : deux exécutions
> peuvent rappeler Mistral ou créer deux rapports. Je le corrigerais avec une clé d’idempotence, une
> contrainte unique et une acquisition atomique du statut.

# 44. Notions voisines : atomicité, transactions et concurrence

## Atomicité

Une opération atomique est indivisible du point de vue du système :

```text
soit tout réussit
soit rien n’est appliqué
```

Exemple souhaité :

```text
créer Recording
créer SessionRecording
valider ensemble
```

Une transaction SQL aide à obtenir cette atomicité.

## Transaction

Une transaction regroupe plusieurs opérations de base.

```python
session.add(recording)
session.add(link)
session.commit()
```

`commit` valide. En cas d’erreur avant validation, un `rollback` annule les changements non validés.

## ACID

### Atomicity

Tout ou rien.

### Consistency

Les contraintes restent valides avant et après la transaction.

### Isolation

Les transactions concurrentes ne se perturbent pas de manière incorrecte.

### Durability

Après commit confirmé, la donnée doit survivre à un redémarrage selon les garanties du moteur.

## Limite entre base et fichier

Une transaction SQLite ne contrôle pas le système de fichiers.

Dans Scribe :

```text
supprimer audio
puis commit DB
```

Si le commit échoue, le fichier est déjà supprimé.

Il n’existe pas de transaction atomique commune simple entre SQLite et le disque.

Solutions :

- état `deletion_pending` ;
- outbox transactionnelle ;
- tâche idempotente ;
- retry ;
- stockage objet avec événements ;
- compensation.

## Compensation

Dans un système distribué, on ne peut pas toujours annuler techniquement. Une action compensatoire
répare l’effet.

Exemple :

- opération A crée une réservation ;
- opération B échoue ;
- compensation annule la réservation.

Cela forme parfois une saga.

## Concurrence

La concurrence signifie que plusieurs opérations progressent sur une même période.

Elle ne signifie pas forcément qu’elles s’exécutent au même instant physique.

Exemples :

- deux uploads ;
- deux workers ;
- deux retraits ;
- utilisateur qui clique deux fois.

## Parallélisme

Le parallélisme signifie que plusieurs tâches s’exécutent réellement en même temps, par exemple sur
plusieurs cœurs ou machines.

```text
concurrence = chevauchement logique
parallélisme = exécution simultanée réelle
```

## Race condition

Une condition de course apparaît lorsque le résultat dépend de l’ordre imprévisible des opérations.

Dans `process_recording` :

```text
worker A lit UPLOADED
worker B lit UPLOADED
worker A met PROCESSING
worker B met PROCESSING
les deux appellent Mistral
```

La garde actuelle ne suffit pas si les lectures arrivent avant les commits.

## Section critique

Partie du code qui lit/modifie une ressource partagée et doit être protégée.

Ici, l’acquisition du traitement est une section critique.

## Verrou pessimiste

Le système verrouille la ligne avant modification. Les autres attendent ou échouent.

Avantage : évite certaines courses.  
Coût : attente et risque de blocage.

SQLite a des limites différentes d’un PostgreSQL managé pour ces usages.

## Verrou optimiste

On lit une version puis on met à jour seulement si elle n’a pas changé.

Exemple conceptuel :

```sql
UPDATE recording
SET status = 'processing'
WHERE id = ? AND status = 'uploaded'
```

Si une seule ligne a changé, le worker a acquis le job. Si zéro, un autre l’a pris.

## Deadlock

Deux transactions se bloquent mutuellement en attendant les verrous de l’autre.

Prévention :

- ordre de verrouillage constant ;
- transactions courtes ;
- timeout ;
- retry contrôlé.

## État ou state

L’état est l’ensemble des valeurs décrivant la situation actuelle.

Dans le dictaphone :

```text
idle -> recording -> paused -> ready -> uploading
```

## Machine à états

Une machine à états définit :

- états possibles ;
- événements ;
- transitions autorisées ;
- actions.

Avantage : empêche les combinaisons incohérentes.

Le code React utilise des chaînes, mais ne formalise pas toutes les transitions.

## Invariant

Une règle qui doit toujours rester vraie.

Exemples :

- un enregistrement appartient à un utilisateur ;
- une réunion ne démarre que si tous les accords sont actifs ;
- un rapport structuré correspond à un seul enregistrement ;
- un fichier supprimé ne doit plus être annoncé comme disponible.

Les tests doivent cibler les invariants.

## Cohérence forte

Une lecture voit immédiatement la dernière écriture confirmée selon les garanties du système.

## Cohérence éventuelle

Les différentes parties peuvent être temporairement en désaccord, puis convergent.

Exemple futur :

- upload accepté ;
- statut `uploaded` ;
- worker traite ;
- quelques secondes plus tard `completed`.

L’interface doit savoir afficher cet état intermédiaire.

## Stateless

Un backend stateless ne dépend pas de la mémoire locale d’une instance entre deux requêtes.

Un JWT aide, mais Scribe n’est pas entièrement stateless :

- SQLite locale ;
- fichiers audio locaux ;
- BackgroundTasks locales.

## Stateful

Un composant stateful conserve un état local nécessaire. SQLite et le dossier audio rendent
l’instance backend stateful.

## Persistance et volatilité

### Persistant

Survit à la fin du processus : base/fichier correctement stocké.

### Volatil

Disparaît :

- variables mémoire ;
- `chunks.current` ;
- Blob navigateur ;
- tâche non durable après crash.

## Durabilité

La durabilité est la capacité des données validées à survivre aux pannes prévues.

Une base managée avec sauvegardes offre davantage de garanties qu’un fichier SQLite sur une instance
éphémère.

# 45. Fiabilité : timeout, retry, backoff et files

## Timeout

Un timeout limite le temps d’attente.

```python
timeout=240
```

Sans timeout, une connexion bloquée peut occuper indéfiniment une ressource.

Un timeout ne dit pas si le serveur distant a exécuté l’opération avant la coupure.

## Retry

Un retry recommence après une erreur temporaire.

Bon pour :

- coupure réseau ;
- 429 ;
- certains 5xx.

Mauvais sans contrôle pour :

- 400 ;
- donnée invalide ;
- opération non idempotente ;
- coût IA répété.

## Backoff exponentiel

On attend de plus en plus :

```text
1 s, 2 s, 4 s, 8 s
```

Cela évite de surcharger un service en panne.

## Jitter

Petit aléa ajouté au délai afin que tous les clients ne réessaient pas au même instant.

## Circuit breaker

Après trop d’échecs, on arrête temporairement les appels au service.

États conceptuels :

- fermé : appels normaux ;
- ouvert : refus rapide ;
- semi-ouvert : test de reprise.

## File de messages

Une file conserve les jobs à traiter.

Elle découple :

- API d’upload ;
- worker IA.

Avantages :

- reprise ;
- lissage de charge ;
- plusieurs workers ;
- accusé de réception ;
- observation des jobs.

## Livraison au moins une fois

Beaucoup de files peuvent livrer un message plusieurs fois. Le worker doit donc être idempotent.

## Livraison au plus une fois

Le message n’est jamais dupliqué, mais peut être perdu.

## Exactement une fois

Garantie globale difficile dans un système distribué. On obtient souvent l’effet métier « exactement
une fois » par idempotence et déduplication.

## Dead-letter queue

Après plusieurs échecs, un message est déplacé dans une file d’erreurs pour analyse, au lieu d’être
réessayé indéfiniment.

## Polling

Le client demande périodiquement :

```text
est-ce que ça a changé ?
```

Avantages :

- simple ;
- HTTP classique.

Limites :

- retard ;
- requêtes inutiles ;
- erreurs silencieuses possibles.

## Server-Sent Events

Le serveur pousse des événements dans une connexion HTTP vers le navigateur, dans un seul sens.

## WebSocket

Connexion bidirectionnelle persistante. Plus temps réel, mais gestion plus complexe.

## Webhook

Un service appelle une URL du projet lorsque le traitement est terminé. Il faut vérifier la
signature et gérer les doublons.

## Fail-open et fail-closed

### Fail-open

En cas d’incertitude, l’action continue.

Le polling actuel ignore une erreur réseau :

```javascript
verify().catch(() => {})
```

Le dictaphone continue. C’est un comportement plutôt fail-open.

### Fail-closed

En cas d’incertitude, on bloque ou arrête.

Pour le consentement, un comportement fail-closed est plus prudent :

- afficher perte de vérification ;
- mettre en pause ;
- arrêter après un court délai ;
- ne jamais uploader sans revalidation.

## Disponibilité

Capacité du service à répondre quand on le demande.

## Fiabilité

Capacité à produire durablement le bon résultat malgré des pannes prévues.

## Résilience

Capacité à absorber une panne et récupérer :

- retry ;
- file ;
- redondance ;
- timeout ;
- reprise.

## Scalabilité verticale

Ajouter CPU/RAM à une machine.

## Scalabilité horizontale

Ajouter des instances.

Scribe doit externaliser base, fichiers et jobs pour scaler horizontalement.

# 46. Sécurité et exploitation — notions complémentaires

## Authentification

Prouver qui est l’utilisateur.

## Autorisation

Vérifier ce qu’il peut faire. `owned_recording` applique une autorisation.

## Validation

Vérifier qu’une entrée respecte un contrat :

- taille ;
- type ;
- présence ;
- format.

## Sanitization

Transformer ou nettoyer une entrée pour un usage particulier. Ce n’est pas la même chose que
valider.

Exemple :

```python
title.strip()
```

retire les espaces aux extrémités, mais ne prouve pas que le titre est sans danger dans tous les
contextes.

## Échappement

Encoder une valeur pour qu’elle reste du texte dans un contexte. React échappe les chaînes dans JSX
par défaut.

## Principe du moindre privilège

Chaque composant ne doit recevoir que les droits nécessaires :

- clé Mistral uniquement backend ;
- utilisateur limité à ses enregistrements ;
- service de stockage limité à son bucket.

## Secret et configuration

Une configuration n’est pas toujours secrète :

- port : configuration ;
- modèle : configuration ;
- clé API : secret.

Tous vivent parfois dans l’environnement, mais ne doivent pas être traités de la même manière.

## Rotation de secret

Remplacer une clé sans interruption, puis révoquer l’ancienne.

Le projet doit prévoir la rotation de :

- clé Mistral ;
- secret Google ;
- mot de passe SMTP ;
- clé JWT/session.

## Rate limiting

Limiter le nombre de requêtes par :

- IP ;
- compte ;
- token ;
- endpoint.

Protège contre :

- bruteforce ;
- spam ;
- coûts IA ;
- déni de service.

## Journal ou log

Un log enregistre un événement technique ou métier.

Il ne faut pas y placer :

- clés ;
- token de consentement ;
- mot de passe ;
- audio ;
- transcription complète sans justification.

## Métrique

Valeur agrégée :

- latence ;
- nombre d’erreurs ;
- taille d’upload ;
- coût ;
- durée de traitement.

## Trace distribuée

Suit une requête à travers plusieurs services avec un identifiant de corrélation.

## Observabilité

Capacité à comprendre l’état du système grâce à :

- logs ;
- métriques ;
- traces.

## Monitoring

Surveillance et alertes basées sur ces signaux.

## Audit trail

Historique métier de décisions sensibles :

- accord ;
- retrait ;
- effacement ;
- accès administratif.

Il doit être minimisé et protégé.

## Sauvegarde

Copie permettant la restauration.

Le droit à l’effacement doit aussi définir le traitement des sauvegardes :

- durée ;
- accès ;
- réintégration ;
- suppression à expiration.

## Chiffrement au repos

Protège les données stockées sur disque ou objet.

## Chiffrement en transit

HTTPS/TLS protège les échanges réseau.

## Reverse proxy contre proxy direct

Un proxy direct agit pour le client vers Internet. Un reverse proxy agit devant les serveurs et
reçoit les requêtes des clients.

# 47. Questions réseau et architecture à apprendre mot pour mot

**Quelqu’un qui possède mon lien localhost peut-il ouvrir mon application ?**  
Pas depuis un autre PC avec ce lien seul. Son `localhost` désigne son propre ordinateur. Sur la même
machine, un autre programme peut tenter l’accès.

**Localhost est-il sécurisé par un mot de passe ?**  
Non. Il limite normalement le routage à la machine, mais n’authentifie rien.

**Quelle différence entre localhost et une IP privée ?**  
Localhost reste dans la machine. Une IP privée identifie la machine sur le réseau local.

**Quelle différence entre IP et port ?**  
L’IP choisit la machine/interface. Le port choisit le service sur cette machine.

**Pourquoi deux ports ?**  
Vite et FastAPI sont deux processus. Vite écoute 5174, FastAPI 8000.

**Qui répond à `/api` quand le navigateur appelle 5174 ?**  
Vite reçoit puis transmet au backend 8000 grâce au proxy.

**Le proxy Vite fonctionne-t-il après `npm run build` ?**  
Non. Il faut un reverse proxy ou une URL d’API dans l’hébergement.

**Pourquoi une URL localhost envoyée par e-mail échoue-t-elle ?**  
Le participant demande le service sur son propre PC, où le serveur et la base n’existent pas.

**Comment partager temporairement sur le Wi-Fi ?**  
Il faudrait écouter sur les interfaces réseau, utiliser l’IP privée, ouvrir le pare-feu et configurer
les URLs. Ce n’est pas un hébergement sûr et le microphone peut exiger HTTPS.

**Que signifie `0.0.0.0` ?**  
Écouter sur toutes les interfaces IPv4. Ce n’est pas l’adresse publique à partager.

**CORS suffit-il à sécuriser le backend ?**  
Non. Il ne remplace jamais authentification, autorisation et validation.

**Pourquoi HTTPS même avec une authentification ?**  
Sans TLS, identifiants, JWT et audio peuvent être interceptés.

**Qu’est-ce que l’idempotence ?**  
La répétition d’une même opération logique ne produit pas un effet supplémentaire incorrect.

**Pourquoi une clé d’idempotence ?**  
Pour reconnaître un retry et ne pas relancer une création, une facturation ou un appel IA.

**POST est-il idempotent ?**  
Pas par défaut. On peut cependant rendre une opération POST idempotente avec une clé et un stockage
de résultat.

**DELETE est-il idempotent si le deuxième appel renvoie 404 ?**  
Oui pour l’effet final : la ressource reste absente.

**Atomicité et idempotence sont-elles identiques ?**  
Non. Atomicité signifie tout ou rien. Idempotence signifie répétition sans effet supplémentaire.

**Concurrence et parallélisme sont-ils identiques ?**  
Non. La concurrence est un chevauchement logique ; le parallélisme est une exécution simultanée.

**Qu’est-ce qu’une race condition ?**  
Un résultat incorrect dépendant de l’ordre imprévisible de plusieurs opérations.

**Pourquoi le worker actuel peut-il traiter deux fois ?**  
Deux workers peuvent lire l’état avant que l’un ait validé `PROCESSING`.

**Pourquoi une file peut-elle livrer deux fois ?**  
Si le worker termine mais ne confirme pas la réception, la file remet le message. Le traitement doit
être idempotent.

**Timeout et retry, différence ?**  
Le timeout arrête l’attente ; le retry recommence. Un timeout ne prouve pas que l’opération distante
n’a pas été effectuée.

**Pourquoi un backoff ?**  
Pour ne pas aggraver une panne en réessayant immédiatement en masse.

**Fail-open et fail-closed ?**  
Fail-open continue en cas de doute ; fail-closed bloque. Le consentement devrait plutôt échouer fermé.
