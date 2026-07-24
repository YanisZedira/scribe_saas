# Yanis — cartographie exacte et entraînement oral de zéro à soutenance

Ce chapitre transforme la lecture précédente en réponses utilisables devant le professeur.

La règle à suivre à l’oral est toujours la même :

1. dire en français courant ce que fait la ligne ;
2. définir immédiatement chaque terme technique ;
3. expliquer pourquoi la ligne existe ;
4. expliquer son effet sur le reste du projet ;
5. reconnaître sa limite réelle ;
6. montrer le fichier et le commit exacts.

## 1. Carte exacte des dix commits

### 1 — Configuration backend

[Commit `2646623`](https://github.com/AshDv/ScribeProject/commit/2646623fc7c4bf83106cc4629ffa934131303012)

Fichiers à montrer :

- [`.gitignore`](https://github.com/AshDv/ScribeProject/blob/2646623fc7c4bf83106cc4629ffa934131303012/.gitignore)
- [`pyproject.toml`](https://github.com/AshDv/ScribeProject/blob/2646623fc7c4bf83106cc4629ffa934131303012/pyproject.toml)
- [`.env.example`](https://github.com/AshDv/ScribeProject/blob/2646623fc7c4bf83106cc4629ffa934131303012/server/.env.example)
- [`config.py`](https://github.com/AshDv/ScribeProject/blob/2646623fc7c4bf83106cc4629ffa934131303012/server/app/config.py)
- [`requirements.txt`](https://github.com/AshDv/ScribeProject/blob/2646623fc7c4bf83106cc4629ffa934131303012/server/requirements.txt)
- [`start.ps1`](https://github.com/AshDv/ScribeProject/blob/2646623fc7c4bf83106cc4629ffa934131303012/start.ps1)

Phrase simple :

« Ce commit sépare les valeurs changeantes du code, empêche Git de prendre les secrets et fixe les outils et versions nécessaires au backend. »

### 2 — Base et point de santé

[Commit `452b4ff`](https://github.com/AshDv/ScribeProject/commit/452b4ff60921cba714272cecdb51713c3d65385a)

- [`db.py`](https://github.com/AshDv/ScribeProject/blob/452b4ff60921cba714272cecdb51713c3d65385a/server/app/db.py)
- [`main.py`](https://github.com/AshDv/ScribeProject/blob/452b4ff60921cba714272cecdb51713c3d65385a/server/app/main.py)

Phrase simple :

« Ce commit ouvre SQLite avec SQLModel, crée les tables au démarrage, ferme les sessions proprement et expose `/api/health` pour vérifier que FastAPI répond. »

### 3 — React et Vite

[Commit `ed08945`](https://github.com/AshDv/ScribeProject/commit/ed08945d27613f7d2942baf3e482465483e338bb)

- [`index.html`](https://github.com/AshDv/ScribeProject/blob/ed08945d27613f7d2942baf3e482465483e338bb/web/index.html)
- [`package.json`](https://github.com/AshDv/ScribeProject/blob/ed08945d27613f7d2942baf3e482465483e338bb/web/package.json)
- [`main.jsx`](https://github.com/AshDv/ScribeProject/blob/ed08945d27613f7d2942baf3e482465483e338bb/web/src/main.jsx)
- [`vite.config.js`](https://github.com/AshDv/ScribeProject/blob/ed08945d27613f7d2942baf3e482465483e338bb/web/vite.config.js)

Phrase simple :

« Ce commit crée le point d’entrée du navigateur, insère React dans le `div root` et configure Vite sur 5174 avec un transfert de `/api` vers FastAPI sur 8000. »

### 4 — Coquille visuelle

[Commit `6104ac5`](https://github.com/AshDv/ScribeProject/commit/6104ac55c5dad4fe4b6d7382a7ea5d17c9862250)

- [`App.jsx`](https://github.com/AshDv/ScribeProject/blob/6104ac55c5dad4fe4b6d7382a7ea5d17c9862250/web/src/App.jsx)
- [`index.css`](https://github.com/AshDv/ScribeProject/blob/6104ac55c5dad4fe4b6d7382a7ea5d17c9862250/web/src/index.css)

Phrase simple :

« Ce commit donne à l’application son premier composant et son système visuel responsive : couleurs partagées, cartes, formulaires, dictaphone, consentement et affichage mobile. »

### 5 — Acceptation et retrait

[Commit `4e21df6`](https://github.com/AshDv/ScribeProject/commit/4e21df68d3c0241f1ca5d9b9751e8aeaf5315daa)

- [`consent_routes.py`](https://github.com/AshDv/ScribeProject/blob/4e21df68d3c0241f1ca5d9b9751e8aeaf5315daa/server/app/consent_routes.py)

Phrase simple :

« Ce commit vérifie tous les accords avant le démarrage, permet le retrait à tout moment et traite la demande d’effacement liée au jeton public. »

### 6 — Page publique de consentement

[Commit `ecd894c`](https://github.com/AshDv/ScribeProject/commit/ecd894ce955b396193fcc1300278517fbd4c3d35)

- [`PrivacyFlows.jsx`](https://github.com/AshDv/ScribeProject/blob/ecd894ce955b396193fcc1300278517fbd4c3d35/web/src/PrivacyFlows.jsx)
- [`api.js`](https://github.com/AshDv/ScribeProject/blob/ecd894ce955b396193fcc1300278517fbd4c3d35/web/src/api.js)

Phrase simple :

« Ce commit affiche au participant ce qui sera traité et lui donne les actions accepter, refuser, retirer et demander l’effacement. »

### 7 — Upload audio

[Commit `2a1dbd0`](https://github.com/AshDv/ScribeProject/commit/2a1dbd0cc227d07739776329f5f517473913f15c)

- [`routes.py`](https://github.com/AshDv/ScribeProject/blob/2a1dbd0cc227d07739776329f5f517473913f15c/server/app/routes.py)

Phrase simple :

« Ce commit reçoit le fichier seulement après les contrôles de compte, réunion et consentements, limite son type et sa taille, fabrique un nom serveur et lance le traitement. »

### 8 — Dictaphone

[Commit `1ae2765`](https://github.com/AshDv/ScribeProject/commit/1ae2765b1bb0b9d585757c781a44ff2f4fc5b428)

- [`MeetingWorkflow.jsx`](https://github.com/AshDv/ScribeProject/blob/1ae2765b1bb0b9d585757c781a44ff2f4fc5b428/web/src/MeetingWorkflow.jsx)
- [`api.js`](https://github.com/AshDv/ScribeProject/blob/1ae2765b1bb0b9d585757c781a44ff2f4fc5b428/web/src/api.js)

Phrase simple :

« Ce commit utilise le microphone natif du navigateur, garde les fragments en mémoire, construit un Blob à l’arrêt et efface les fragments si un retrait de consentement est détecté. »

### 9 — Compte rendu Mistral

[Commit `1f88e83`](https://github.com/AshDv/ScribeProject/commit/1f88e83fc774214614d25ddcfb07ea9ae989a4f1)

- [`llm.py`](https://github.com/AshDv/ScribeProject/blob/1f88e83fc774214614d25ddcfb07ea9ae989a4f1/server/app/llm.py)

Phrase simple :

« Ce commit définit un contrat JSON avec Pydantic, envoie la transcription à Mistral, valide la réponse puis vérifie que chaque segment est couvert exactement une fois. »

### 10 — Pipeline complet

[Commit `15511bd`](https://github.com/AshDv/ScribeProject/commit/15511bdaf809f905b2a76ab273e9f2f2be256469)

- [`processing.py`](https://github.com/AshDv/ScribeProject/blob/15511bdaf809f905b2a76ab273e9f2f2be256469/server/app/processing.py)

Phrase simple :

« Ce commit relie l’audio à Voxtral, puis le texte à Mistral, stocke le rapport, change le statut et supprime le fichier audio temporaire. »

## 2. Comment répondre quand le professeur pointe une ligne inconnue

Ne commence jamais par réciter un nom d’outil. Suis ce modèle :

« Cette ligne reçoit telle valeur. Le signe ici veut dire ceci. L’ordinateur effectue ensuite cette action. Elle est placée dans cette fonction parce que le contrôle doit avoir lieu avant telle étape. Le reste du projet dépend d’elle de cette manière. Si on la retire, voici le problème concret. Sa limite est celle-ci. »

Exemple avec :

```python
if not participants or not all(is_active(item) for item in participants):
```

Réponse complète :

« La ligne vérifie deux situations. `not participants` devient vrai si la liste est vide. `all` examine chaque participant et exige que la fonction `is_active` renvoie vrai pour chacun. Le second `not` inverse ce résultat, donc la condition devient vraie dès qu’au moins une personne n’a pas un accord actif. `or` signifie qu’une liste vide ou un seul accord manquant suffit pour refuser. Cette ligne est placée avant le changement vers l’état d’enregistrement, car le dictaphone ne doit jamais s’ouvrir d’abord puis vérifier ensuite. Si on la retire, une demande directe à l’API pourrait contourner l’interface. »

## 3. Exercice : expliquer une importation

Ligne :

```python
from pathlib import Path
```

Mauvaise réponse : « C’est Path. »

Bonne réponse :

« Python permet de découper un projet en modules, c’est-à-dire en fichiers de code réutilisables. `pathlib` est un module fourni avec Python pour manipuler les chemins. `from` indique le module source, `import` demande un élément précis, et `Path` est la classe importée. Une classe est un modèle de fabrication d’objets. Nous transformons ensuite un texte de chemin en instance `Path` pour le rendre absolu, vérifier qu’il reste dans le dossier audio, tester son existence et supprimer le fichier. »

## 4. Exercice : expliquer une fonction

Ligne :

```python
def token_hash(token: str) -> str:
```

Réponse :

« `def` annonce une fonction, donc un ensemble d’instructions que l’on pourra appeler. `token_hash` est son nom en snake_case : mots minuscules séparés par un trait de soulignement, convention Python. Entre parenthèses, `token` est le paramètre, la valeur donnée lors de l’appel. `: str` indique qu’on attend du texte. La flèche `-> str` annonce que la fonction renvoie du texte. Le deux-points ouvre le bloc indenté. Cette fonction centralise le calcul SHA-256 afin que la création et la vérification utilisent exactement la même méthode. »

## 5. Exercice : expliquer une variable

Ligne :

```python
covered = [item.segment_id for item in result.coverage]
```

Réponse :

« Une variable est un nom qui permet de retrouver une valeur. Ici le nom `covered` recevra une liste. Les crochets créent cette liste. La partie `for item in result.coverage` parcourt chaque objet de couverture. `item.segment_id` lit son identifiant. Le résultat est donc la liste de tous les identifiants que Mistral affirme avoir couverts. Elle est ensuite comparée aux identifiants d’entrée pour détecter un oubli, un ajout ou un doublon. »

## 6. Exercice : expliquer un dictionnaire

Ligne :

```python
payload = {"participants": participant_names}
```

Réponse :

« Un dictionnaire Python associe des clés à des valeurs. Les accolades l’ouvrent. `"participants"` est la clé textuelle; les deux-points l’associent à la variable `participant_names`, qui contient une liste. Ce dictionnaire peut ensuite être transformé en JSON et envoyé à l’API. Une liste est une suite ordonnée; un dictionnaire retrouve une valeur par son nom de clé. »

## 7. Exercice : expliquer une classe et une instance

Ligne :

```python
class ActionItem(BaseModel):
```

Réponse :

« Une classe est un modèle décrivant la forme et le comportement d’objets. `ActionItem` est la classe représentant une action de réunion. Elle hérite de `BaseModel`, donc elle récupère les capacités de validation Pydantic. Quand Pydantic lit une action JSON valide, il crée une instance : un objet concret contenant par exemple la tâche, le responsable et les segments. La classe est le plan; l’instance est l’objet fabriqué d’après le plan. »

## 8. Exercice : expliquer un constructeur

Ligne :

```javascript
recorder.current = new MediaRecorder(stream.current);
```

Réponse :

« `MediaRecorder` est une classe fournie par le navigateur. Le mot `new` appelle son constructeur, c’est-à-dire le mécanisme qui fabrique une nouvelle instance. L’argument `stream.current` est le flux du microphone que cette instance devra enregistrer. L’objet créé est rangé dans `recorder.current` afin de pouvoir ensuite appeler `start`, `pause`, `resume` et `stop`. »

## 9. Exercice : expliquer une condition

Ligne :

```javascript
if (current.status !== "recording" || !current.all_consented)
```

Réponse :

« `if` exécute son bloc seulement si la condition est vraie. `!==` signifie que le statut est différent du texte `recording`. `||` signifie “ou”. `!` inverse la valeur suivante. La condition est donc vraie si le serveur n’autorise plus l’enregistrement ou si tous les consentements ne sont plus actifs. Un seul de ces problèmes suffit pour arrêter et effacer le son local. »

## 10. Exercice : expliquer `async` et `await`

Ligne :

```javascript
stream.current = await navigator.mediaDevices.getUserMedia({ audio: true });
```

Réponse :

« Demander le microphone prend du temps, car le navigateur peut afficher une autorisation. La fonction est déclarée `async` pour pouvoir utiliser `await`. `await` suspend seulement la suite de cette fonction jusqu’au résultat; il ne bloque pas toute l’interface. Si l’utilisateur accepte, la promesse fournit un flux audio. S’il refuse, une erreur est envoyée au `catch`. »

Une promesse est un objet JavaScript représentant un résultat futur : en attente, réussi ou échoué.

## 11. Exercice : expliquer un effet React

Ligne :

```javascript
useEffect(() => {
  const timer = setInterval(verify, 3000);
  return () => clearInterval(timer);
}, [state]);
```

Réponse :

« Un composant React calcule d’abord ce qui doit être affiché. `useEffect` lance ensuite une action extérieure à ce calcul, ici un minuteur. `setInterval` répète la vérification toutes les trois secondes. La fonction renvoyée est le nettoyage : elle supprime l’intervalle lorsque l’état change ou que le composant disparaît. La liste `[state]` dit que l’effet dépend de l’état. Sans nettoyage, plusieurs minuteurs pourraient s’accumuler et envoyer des demandes inutiles. »

## 12. Exercice : expliquer une requête SQLModel

Ligne :

```python
select(Recording).where(Recording.owner_id == user.id)
```

Réponse :

« SQL est le langage de requête des bases relationnelles. SQLModel permet de construire la demande avec des classes Python. `select(Recording)` signifie que l’on veut des lignes de la table des enregistrements. `where` ajoute un filtre. La comparaison garde seulement les lignes dont le propriétaire correspond à l’utilisateur connecté. C’est le contrôle d’autorisation qui empêche un compte de lire les enregistrements d’un autre. »

## 13. ORM expliqué sans jargon

ORM signifie « Object-Relational Mapping », ou correspondance objet-relationnelle.

Une base SQL organise les informations dans des tables, lignes et colonnes.

Python organise le code avec des objets et classes.

L’ORM fait le pont :

- une classe peut représenter une table ;
- une instance peut représenter une ligne ;
- un attribut peut représenter une colonne.

SQLModel est l’ORM utilisé.

L’ORM ne supprime pas la nécessité de comprendre SQL. Il construit les ordres et peut produire des requêtes inefficaces ou des problèmes de transaction si on l’utilise mal.

## 14. SQL contre NoSQL

SQL désigne les bases relationnelles. Elles organisent les données en tables liées par des identifiants et utilisent un schéma défini.

NoSQL regroupe plusieurs familles non relationnelles : documents JSON, clé-valeur, colonnes larges ou graphes.

Scribe utilise SQL parce que les comptes, réunions, participants, consentements et enregistrements possèdent des relations claires. On veut par exemple garantir qu’un enregistrement appartient à un utilisateur et à une réunion.

SQLite est un moteur SQL dans un fichier. PostgreSQL serait un moteur SQL serveur plus adapté à la production partagée.

## 15. API REST expliquée

API signifie interface de programmation. C’est une manière définie pour qu’un programme demande quelque chose à un autre.

REST est un style d’API organisé autour de ressources et des méthodes HTTP.

Dans Scribe :

- `GET /api/recordings` lit une collection ;
- `POST /api/recordings` crée un enregistrement à traiter ;
- `GET /api/recordings/{id}` lit un élément ;
- `DELETE /api/recordings/{id}` le supprime.

HTTP est le protocole de messages utilisé par le Web.

Une méthode indique l’intention. Une URL indique la ressource. Un statut indique le résultat. JSON ou multipart transporte les données.

REST n’est pas une obligation technique de FastAPI; c’est la manière dont les routes sont conçues.

## 16. Autres types d’API

GraphQL utilise souvent une seule adresse où le client décrit précisément les champs voulus. Cela réduit parfois les réponses trop grandes mais ajoute un langage de requête et des contrôles de complexité.

RPC appelle des opérations distantes comme des fonctions, par exemple `StartMeeting`.

WebSocket maintient une connexion bidirectionnelle ouverte. Le serveur peut pousser un événement au navigateur sans attendre une nouvelle demande. Cela pourrait remplacer le polling de consentement.

Webhook est une demande envoyée automatiquement par un service vers une adresse de notre serveur lorsqu’un événement se produit.

SDK est une bibliothèque qui enveloppe une API avec des fonctions prêtes à l’emploi.

Scribe utilise principalement une API REST et appelle Mistral directement avec HTTPX.

## 17. JavaScript vanilla

« Vanilla JavaScript » signifie JavaScript sans bibliothèque ou framework supplémentaire.

Le dictaphone utilise les API natives du navigateur — `MediaRecorder`, `Blob`, `FormData` — mais il les utilise dans React. Le projet n’est donc pas une application entièrement en JavaScript vanilla.

React ne remplace pas JavaScript. Le code React est toujours JavaScript, avec JSX et les fonctions de React.

## 18. TypeScript contre JavaScript

JavaScript est exécuté directement après préparation par le navigateur ou Node.

TypeScript ajoute une syntaxe d’annotations de types et est transformé en JavaScript avant exécution.

Exemple TypeScript :

```typescript
function formatTime(seconds: number): string
```

Le projet frontend utilise JavaScript avec fichiers `.jsx`, pas TypeScript. Les annotations `: str` du backend sont du Python et n’ont rien à voir avec TypeScript.

TypeScript pourrait détecter avant l’exécution l’appel d’une fonction avec un mauvais type. Il ajoute aussi une étape et des définitions de types. Pour un MVP court, JavaScript réduit la configuration; pour une grande équipe, TypeScript peut sécuriser les contrats frontend.

## 19. PEP 8

PEP signifie « Python Enhancement Proposal », une proposition d’évolution ou de convention Python.

PEP 8 est le guide de style du code Python.

Il recommande notamment :

- variables et fonctions en `snake_case`;
- classes en `PascalCase`;
- constantes en `UPPER_CASE`;
- imports organisés ;
- indentation de quatre espaces ;
- lignes raisonnablement courtes ;
- espaces cohérents.

PEP 8 ne garantit pas que le programme fonctionne. C’est une convention de lisibilité.

Le projet configure Ruff avec une longueur de 100 caractères. PEP 8 cite traditionnellement une limite plus courte, mais une équipe peut documenter sa convention.

## 20. Versions Python

Dans `3.12`, `3` est la version majeure et `12` la version mineure.

Une nouvelle version mineure de Python peut ajouter des fonctionnalités et retirer des éléments précédemment annoncés comme obsolètes. Elle n’est pas une simple correction anodine.

Les corrections apparaissent dans un troisième nombre, par exemple `3.12.4`.

Dire « le chiffre rond est une mise à jour majeure » n’est pas assez précis. Dans le versionnage de Python, passer de 3 à 4 serait majeur; passer de 3.11 à 3.12 est mineur mais peut demander des vérifications de compatibilité.

## 21. Annotation de fonction Python

Dans :

```python
def get_session() -> Generator[Session, None, None]:
```

`-> ...` est l’annotation du résultat.

Les annotations documentent les types, aident les outils et sont utilisées par des bibliothèques comme Pydantic ou FastAPI.

Python reste un langage dynamiquement typé : une variable peut recevoir différents types à l’exécution. Une annotation n’est pas toujours une interdiction automatique.

## 22. Clé API

Une clé API est un secret permettant à un service d’identifier le compte ou projet qui appelle.

Dans Scribe, la clé Mistral se trouve dans `.env`, est lue par le backend et envoyée dans l’en-tête `Authorization`.

Elle ne doit pas être dans React, GitHub, une capture d’écran ou un message public.

Une clé exposée doit être révoquée et remplacée. La supprimer d’un dernier commit ne suffit pas si elle reste dans l’historique Git.

Une clé API n’identifie pas forcément l’utilisateur final. Elle identifie le compte de service qui paiera et subira les limites.

## 23. Fonction de hachage

Une fonction de hachage transforme une entrée de taille quelconque en une empreinte de taille fixe.

SHA-256 est utilisé pour le jeton de consentement.

Propriétés attendues :

- même entrée, même empreinte ;
- difficile de retrouver l’entrée depuis l’empreinte ;
- difficile de trouver deux entrées avec la même empreinte.

Pour un mot de passe, SHA-256 seul n’est pas adapté parce qu’il est trop rapide. Bcrypt ajoute un coût volontairement lent et un sel aléatoire.

Un sel est une valeur aléatoire ajoutée au calcul pour empêcher que deux mêmes mots de passe aient facilement la même empreinte et pour rendre les tables pré-calculées moins utiles.

## 24. OAuth 2.0, OpenID Connect et SSO

OAuth 2.0 est un cadre d’autorisation : permettre à une application d’obtenir un accès limité sans recevoir le mot de passe Google.

OpenID Connect ajoute l’identité au-dessus d’OAuth 2.0. Il fournit des informations vérifiables sur l’utilisateur connecté.

SSO signifie « Single Sign-On » : l’utilisateur réutilise une identité existante pour accéder à Scribe.

Dans le projet, Authlib prépare la redirection Google et récupère le profil. Le backend associe l’identité externe à un utilisateur local.

Le `client_id` identifie Scribe. Le `client_secret` prouve l’application côté serveur. Le secret ne doit pas être dans le navigateur.

## 25. Localhost expliqué complètement

`localhost` est un nom spécial qui désigne la machine depuis laquelle il est utilisé.

Sur le PC de Yanis, `http://localhost:5174` désigne le port 5174 du PC de Yanis.

Sur le PC du professeur, la même adresse désigne le PC du professeur, pas celui de Yanis.

Une autre personne n’accède donc pas automatiquement au serveur local en recevant le lien.

Pour rendre le service accessible :

- le programme doit écouter sur une interface réseau adaptée, pas seulement la boucle locale ;
- le pare-feu doit autoriser le port ;
- la personne utilise l’adresse IP ou le nom public de la machine ;
- le réseau doit permettre la route ;
- pour Internet, un hébergement, un domaine et HTTPS sont normalement nécessaires.

## 26. Adresse IP et port

Une adresse IP identifie une interface sur un réseau.

Un port identifie un service à l’intérieur de la machine. On peut comparer l’IP à l’adresse d’un immeuble et le port au numéro d’une porte, en sachant que cette comparaison est simplifiée.

Scribe utilise localement :

- 5174 pour Vite ;
- 8000 pour Uvicorn/FastAPI.

Deux programmes ne peuvent généralement pas écouter simultanément sur le même couple adresse-port.

Un port ne stocke rien. C’est un numéro utilisé pour acheminer les connexions vers le bon processus.

## 27. HTTP et HTTPS

HTTP décrit les demandes et réponses du Web.

HTTPS est HTTP protégé par TLS.

TLS chiffre la communication en transit et vérifie normalement l’identité du serveur grâce à un certificat.

HTTPS ne chiffre pas automatiquement les données dans la base ni sur le disque. Il protège le trajet réseau.

Les API microphone sont généralement limitées aux contextes sécurisés, avec une exception pour `localhost`.

## 28. Cookie, localStorage et jeton

Un cookie est une petite donnée que le navigateur peut renvoyer automatiquement à un serveur selon ses règles.

`localStorage` est un stockage de textes lié à l’origine et accessible au JavaScript de la page.

Le projet place le jeton d’accès Scribe dans `localStorage`.

Avantage : simplicité pour le MVP.

Risque : si un code JavaScript malveillant est exécuté sur la page par une faille XSS, il peut lire le jeton.

XSS signifie injection de script dans une page. Une alternative est un cookie `HttpOnly`, inaccessible au JavaScript, avec des protections CSRF adaptées.

CSRF est une attaque où un autre site pousse le navigateur connecté à envoyer une demande non voulue.

## 29. CORS

CORS signifie « Cross-Origin Resource Sharing ».

Le navigateur considère que le frontend 5174 et le backend 8000 sont des origines différentes parce que le port change.

Le backend indique quelles origines ont le droit de lire ses réponses depuis un navigateur.

CORS n’authentifie pas l’utilisateur et n’empêche pas un programme serveur d’appeler l’API.

## 30. Proxy Vite

Le proxy reçoit les demandes `/api` sur 5174 et les transfère vers 8000.

Le frontend peut donc utiliser des chemins relatifs.

Le proxy simplifie le développement. En production, il faut une règle d’hébergement équivalente ou une adresse publique configurée.

## 31. Docker et Dockerfile

Docker exécute une application dans un conteneur. Un conteneur regroupe le code, les bibliothèques et une vue isolée de l’environnement.

Un Dockerfile est un fichier de recette décrivant comment construire l’image du conteneur :

- image de départ ;
- fichiers copiés ;
- dépendances installées ;
- commande de lancement.

Ce projet S1 n’utilise pas de Dockerfile dans les commits Yanis étudiés. Il ne faut pas prétendre le contraire.

Le symbole `$` n’a pas le même sens partout :

- en PowerShell, `$name` lit une variable ;
- dans un shell Unix, `$NAME` lit une variable ;
- en JavaScript dans une chaîne modèle, `${value}` insère une expression.

Un caractère n’a donc pas un sens universel; il dépend du langage.

## 32. Harness IA

Un harness IA est l’environnement qui entoure un modèle pour le rendre utile à une tâche.

Il peut gérer :

- le prompt ;
- les outils autorisés ;
- les fichiers accessibles ;
- la mémoire ;
- les validations ;
- les nouvelles tentatives ;
- les journaux ;
- les limites de sécurité.

Claude Code ou Codex sont des exemples d’agents/harness de développement autour de modèles.

Dans Scribe, `llm.py` constitue un petit harness métier : prompt système, schéma Pydantic, paramètres, appel HTTP, transformation d’erreurs et contrôle de couverture.

## 33. Serverless

Serverless ne signifie pas « aucun serveur ». Des serveurs existent, mais le fournisseur gère leur démarrage et leur capacité.

L’équipe déploie des fonctions ou services déclenchés à la demande.

Le S1 local n’est pas encore réellement serverless à cause de SQLite, du disque local et des tâches en processus.

Pour évoluer :

- frontend statique sur CDN ;
- API dans des fonctions ou conteneurs gérés ;
- base PostgreSQL gérée ;
- stockage objet ;
- file durable ;
- fonctions de traitement ;
- secrets dans un coffre.

Un CDN distribue les fichiers frontend depuis des emplacements proches des utilisateurs.

Un stockage objet conserve des fichiers par clé dans un service partagé.

Une file durable garde les travaux même si un processus s’arrête.

## 34. Idempotence

Une opération est idempotente quand la répéter mène au même état final.

Exemple simple : « mettre le statut à STOPPED » est logiquement idempotent si rien d’autre ne change.

Dans le code, l’heure `stopped_at` est recalculée à chaque appel, donc la réponse exacte change.

L’upload POST n’est pas idempotent : deux appels peuvent créer deux enregistrements.

Pour rendre une création idempotente, le client peut fournir une clé unique; le serveur mémorise la première réponse et renvoie la même lors d’une répétition.

L’idempotence est importante quand un réseau coupe après l’envoi : le client ne sait pas si le serveur a traité et peut recommencer.

## 35. Transaction

Une transaction regroupe des opérations de base.

`commit` valide. En cas d’échec avant validation, un rollback peut annuler les modifications de la transaction.

Le fichier audio sur le disque et l’appel Mistral ne font pas automatiquement partie de la transaction SQL.

C’est pourquoi supprimer le fichier puis échouer au commit crée une incohérence.

## 36. DRY

DRY signifie « Don’t Repeat Yourself ».

Il ne demande pas de supprimer toute répétition visuelle. Il demande d’éviter plusieurs sources indépendantes pour la même règle.

Exemples réussis :

- `owned_recording` centralise la propriété ;
- `settings` centralise les valeurs ;
- le modèle Pydantic produit et valide le schéma ;
- `PublicShell` centralise le cadre visuel.

Exemple améliorable :

- plusieurs blocs répètent `json.dumps([item.model_dump() ...])`.

Une abstraction trop compliquée peut être pire que trois lignes répétées. DRY doit réduire le risque de divergence, pas cacher le code.

## 37. KISS

KISS signifie « Keep It Simple, Stupid », autrement dit garder la solution simple.

Simple ne signifie pas court à tout prix.

Un JSX entier sur une ligne possède peu de lignes physiques mais est plus difficile à lire.

Une solution KISS :

- utilise les API natives du navigateur ;
- évite une architecture d’agents inutile ;
- sépare les grandes responsabilités ;
- garde des noms explicites ;
- refuse les cas invalides tôt ;
- rend le flux évident.

La sécurité et le consentement nécessaires ne doivent pas être retirés sous prétexte de simplicité.

## 38. Code de statut HTTP à connaître

`200` : demande réussie.

`201` : ressource créée.

`202` : demande acceptée, traitement pas terminé.

`204` : succès sans contenu de réponse.

`400` : demande invalide.

`401` : utilisateur non authentifié ou preuve invalide.

`403` : authentifié mais interdit.

`404` : ressource introuvable; peut aussi masquer une ressource étrangère.

`409` : conflit avec l’état actuel.

`413` : contenu trop volumineux.

`415` : format de média non accepté.

`422` : données ne respectant pas le modèle attendu, souvent généré par FastAPI/Pydantic.

`500` : erreur interne non prévue.

`503` : service nécessaire indisponible ou non configuré.

## 39. Questions rapides et réponses

**Qu’est-ce qu’une bibliothèque ?**  
Du code réutilisable que notre programme appelle. React, HTTPX et Pydantic sont des bibliothèques.

**Qu’est-ce qu’un framework ?**  
Une structure qui organise l’application et appelle notre code à certains moments. FastAPI agit comme framework backend. React se présente comme bibliothèque, même s’il structure fortement l’interface.

**Qu’est-ce qu’une route ?**  
L’association d’une méthode HTTP, d’une adresse et d’une fonction.

**Qu’est-ce qu’une table ?**  
Une structure de base relationnelle composée de colonnes définies et de lignes de données.

**Qu’insère-t-on ?**  
Des lignes. Par exemple une instance `Recording` devient une ligne après `session.add` et `commit`.

**Qu’est-ce qu’une clé primaire ?**  
La valeur qui identifie de manière unique une ligne.

**Qu’est-ce qu’une clé étrangère ?**  
Une valeur qui référence la clé d’une autre table pour créer une relation.

**Qu’est-ce que JSON ?**  
Un format texte structuré composé d’objets, listes, textes, nombres, booléens et valeurs nulles.

**Qu’est-ce qu’un module ?**  
Un fichier de code importable.

**Qu’est-ce qu’un paquet ?**  
Un ensemble organisé de modules.

**Qu’est-ce qu’un objet ?**  
Une valeur regroupant des données et souvent des méthodes.

**Qu’est-ce qu’une méthode ?**  
Une fonction attachée à un objet ou une classe, comme `path.exists()`.

**Qu’est-ce qu’un paramètre ?**  
Le nom prévu dans la définition d’une fonction.

**Qu’est-ce qu’un argument ?**  
La valeur réellement donnée lors de l’appel.

**Qu’est-ce qu’une exception ?**  
Un objet signalant qu’une opération normale ne peut pas continuer.

**Qu’est-ce qu’un `try/catch` ou `try/except` ?**  
Une structure qui tente une action puis traite certaines erreurs prévues.

**Qu’est-ce qu’un booléen ?**  
Une valeur vraie ou fausse.

**Qu’est-ce que `None`, `null` ?**  
La représentation d’une absence de valeur en Python ou JSON/JavaScript.

**Qu’est-ce qu’un linter ?**  
Un relecteur automatique du code. Ruff détecte des erreurs et incohérences Python.

**Qu’est-ce qu’un test unitaire ?**  
Un test automatique d’une petite unité de comportement, isolée autant que possible.

**Qu’est-ce que la CI ?**  
L’intégration continue : un service lance automatiquement contrôles et tests après un push ou une pull request.

**CI signifie-t-elle que le programme est sans bug ?**  
Non. Elle prouve seulement que les contrôles définis ont réussi.

## 40. Simulation de questions agressives du professeur

### « Vous dites RGPD parfait. Prouvez-le. »

Réponse :

« Je ne dirais pas “parfait” uniquement grâce au code. Je peux prouver les mesures présentes : information avant traitement, dates et versions de consentement, blocage backend, retrait, effacement applicatif, suppression audio et contrôle de propriété. Je reconnais ce qui manque pour une conformité complète : analyse juridique de la base légale, registre, DPA vérifié, hébergement final, rétention automatique, sauvegardes, expiration de lien, gestion des violations et preuve organisationnelle. »

### « Votre diarisation fonctionne vraiment ? »

Réponse :

« Le pipeline consomme les segments fournis par la fonction de transcription et le rapport conserve leurs étiquettes et identifiants. L’association à un vrai nom n’est autorisée par le prompt qu’après identification explicite. Cela ne garantit pas une précision parfaite : il faut mesurer le taux d’erreur sur des réunions avec chevauchement, bruit et accents. `llm.py` ne sépare pas acoustiquement les voix; cette partie se trouve dans la transcription. »

### « Pourquoi votre code est-il KISS ? »

Réponse :

« Le dictaphone utilise directement les API natives `getUserMedia`, `MediaRecorder`, `Blob` et `FormData`, sans bibliothèque supplémentaire. Le LLM est un seul appel HTTP avec un modèle Pydantic réutilisé. Mais je ne confonds pas KISS avec nombre minimal de lignes : le CSS et certains JSX sont trop compressés et gagneraient à être reformattés. »

### « Pourquoi ce n’est pas serverless ? »

Réponse :

« Le code local utilise SQLite, un fichier audio sur le disque du processus et une tâche FastAPI en mémoire. Une autre instance ne verrait pas forcément ces fichiers et un redémarrage perdrait la tâche. Le passage serverless exige une base partagée, un stockage objet et une file durable. »

### « Votre résumé est-il fidèle ? »

Réponse :

« Le prompt interdit l’invention, le schéma exige des segments sources, Pydantic valide la structure et Python vérifie la couverture unique de tous les segments. Ces mesures améliorent l’auditabilité mais ne prouvent pas la vérité sémantique. Il faut encore des tests sur un jeu de référence et une vérification que chaque élément est réellement supporté par les segments cités. »

### « Pourquoi stocker le jeton dans localStorage ? »

Réponse :

« C’est un choix simple de MVP. Il permet de conserver la connexion après un rechargement. Sa limite est qu’un script injecté pourrait le lire. Une production plus forte utiliserait un cookie HttpOnly, Secure et SameSite avec une défense CSRF. »

### « Combien de lignes fait le dictaphone ? »

Réponse :

« Le commit ajoute 223 lignes nettes au total, principalement un fichier de parcours de 217 lignes et 11 lignes dans l’API, avec des suppressions de l’ancienne version. Le cœur MediaRecorder tient en moins de lignes, mais compter seulement ce cœur ignorerait consentement, erreurs, nettoyage, interface et upload. »

## 41. Test final : savoir expliquer sans regarder

Yanis doit pouvoir dessiner ceci :

```text
Navigateur 5174
  │
  ├─ React affiche les écrans
  ├─ MediaRecorder capture le micro
  ├─ Blob garde le son en mémoire
  └─ FormData envoie POST /api/recordings
          │
          ▼
FastAPI 8000
  ├─ authentifie le compte
  ├─ vérifie propriétaire + consentements
  ├─ limite type + taille
  ├─ écrit temporairement le fichier
  └─ lance process_recording
          │
          ├─ Voxtral : audio → texte + segments
          ├─ Mistral : segments → JSON structuré
          ├─ Pydantic : contrôle la forme
          ├─ SQLModel : stocke transcript + rapport
          └─ disque : supprime l’audio
```

Puis expliquer chaque flèche :

- qui lance l’action ;
- quel format traverse la flèche ;
- quel contrôle a lieu avant ;
- ce qui est stocké après ;
- ce qui se passe si l’action échoue.

## 42. Dernière réponse de synthèse

« Ma partie couvre la fondation backend, le démarrage de la base et de l’API, la fondation React/Vite et le design, le consentement public, l’upload contrôlé, le dictaphone, le rapport Mistral structuré et leur pipeline. Je peux montrer chaque commit exact. Je comprends les mécanismes, pas seulement les noms : la configuration est validée par Pydantic; SQLModel relie objets et tables; React recalcule l’affichage depuis l’état; MediaRecorder produit des fragments; Blob les rassemble; FastAPI contrôle la demande; HTTPX appelle Mistral; le schéma Pydantic contraint la réponse; le pipeline stocke le texte et supprime l’audio. Je peux aussi expliquer les limites : localStorage, polling silencieux, jeton sans expiration, MIME déclaré, fichier en mémoire, tâche non durable, SQLite local, absence d’idempotence complète et validation sémantique encore insuffisante. »

