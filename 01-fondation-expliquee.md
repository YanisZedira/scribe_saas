# Yanis — les fondations du projet expliquées sans supposer de connaissances

Ce chapitre explique les deux premiers commits de Yanis :

- [`2646623 — chore(api): add backend configuration`](https://github.com/AshDv/ScribeProject/commit/2646623fc7c4bf83106cc4629ffa934131303012)
- [`452b4ff — feat(api): initialize database and health endpoint`](https://github.com/AshDv/ScribeProject/commit/452b4ff60921cba714272cecdb51713c3d65385a)

Le premier commit prépare les réglages et les outils du projet. Le second crée le point de départ du serveur, ouvre la base de données et ajoute une adresse très simple permettant de vérifier que le serveur répond.

## 1. Ce que signifie le nom du premier commit

```text
chore(api): add backend configuration
```

`chore` est un mot anglais utilisé dans les messages Git pour signaler un travail technique nécessaire qui n’est pas encore une fonctionnalité visible par l’utilisateur. Ici, l’utilisateur ne voit pas encore un bouton supplémentaire : on prépare le terrain.

`api` indique la zone du projet concernée. Une API est une porte d’entrée permettant à deux programmes de communiquer. Dans Scribe, le navigateur envoie des demandes au serveur grâce à cette porte.

`add backend configuration` signifie « ajouter la configuration du serveur ». Le backend est la partie exécutée côté serveur : elle reçoit les demandes, applique les règles, parle à la base de données et appelle Mistral. La configuration regroupe les valeurs qui peuvent changer selon l’ordinateur ou l’environnement, par exemple l’adresse de la base de données ou la taille maximale d’un fichier.

Les deux-points et les parenthèses ne sont pas compris par Python. Ils appartiennent seulement à une convention de nommage des commits appelée « Conventional Commits ». Cette convention rend l’historique plus facile à lire.

## 2. Le fichier `.gitignore`

Git garde l’historique des fichiers du projet. Mais certains fichiers ne doivent jamais être envoyés sur GitHub : les mots de passe, les fichiers temporaires, la base locale et les milliers de fichiers téléchargés par les outils.

Le nom `.gitignore` signifie littéralement « ce que Git doit ignorer ». Le point au début du nom indique un fichier normalement caché par Windows, macOS ou Linux.

### Ligne `# Python`

Le caractère `#` commence un commentaire. Un commentaire est un texte destiné aux humains. Git ne traite pas cette ligne comme une règle. Elle sert uniquement de titre pour annoncer que les règles suivantes concernent Python.

### Ligne `__pycache__/`

Quand Python exécute un fichier, il peut fabriquer une version intermédiaire plus rapide à relire. Il range cette version dans un dossier nommé `__pycache__`.

Les deux traits de soulignement avant et après `pycache` font partie du nom choisi par Python. Le `/` final indique que l’on parle d’un dossier. Cette ligne empêche Git de conserver ces fichiers fabriqués automatiquement. Les envoyer n’apporterait rien : ils peuvent être recréés et varient selon la version de Python.

Si cette ligne était retirée, Git pourrait afficher de nombreux fichiers inutiles comme changements. Cela rendrait les commits confus sans améliorer le programme.

### Ligne `*.py[cod]`

L’étoile `*` signifie « n’importe quel début de nom ». Les crochets `[cod]` signifient « une seule des lettres c, o ou d ». La règle correspond donc notamment aux fichiers `.pyc`, `.pyo` et `.pyd`, qui sont des fichiers techniques liés à Python.

Cette écriture évite de répéter trois règles presque identiques. Elle ne supprime aucun fichier : elle dit seulement à Git de ne pas les suivre.

### Lignes `.venv/` et `venv/`

Un environnement virtuel Python est un dossier contenant une copie isolée de Python et les bibliothèques installées pour un projet. « Isolé » signifie que les versions utilisées par Scribe ne modifient pas celles d’un autre projet.

Les développeurs nomment souvent ce dossier `.venv` ou `venv`. Les deux variantes sont ignorées. Ce dossier peut peser lourd et peut être reconstruit à partir de `requirements.txt`, donc il n’a pas sa place dans Git.

### Ligne `*.egg-info/`

Certains outils Python créent un dossier se terminant par `.egg-info` pour stocker des informations sur un paquet Python : son nom, sa version et ses dépendances. L’étoile accepte n’importe quel nom avant cette terminaison.

Ce contenu étant généré automatiquement, il est ignoré.

### Ligne `# Secrets & DB`

C’est un commentaire servant de titre. `Secrets` désigne les informations confidentielles, par exemple une clé API. `DB` est l’abréviation anglaise de « database », donc « base de données ».

### Ligne `.env`

Le fichier `.env` contient les vraies valeurs propres à l’ordinateur : clé Mistral, mot de passe SMTP, secret de session, etc. Une clé API ressemble à un mot de passe donné à un programme pour qu’un service externe reconnaisse le compte qui effectue la demande.

Cette règle est cruciale : elle empêche normalement d’ajouter `.env` à Git par accident. « Normalement » est important, car si le fichier avait déjà été suivi par Git avant l’ajout de cette règle, il faudrait aussi le retirer de l’historique et changer les secrets exposés.

### Ligne `.env.*`

Cette règle ignore tous les noms commençant par `.env.` : par exemple `.env.local` ou `.env.production`. L’étoile signifie que n’importe quel texte peut suivre le point.

Ces fichiers peuvent eux aussi contenir des secrets ou des réglages propres à un environnement.

### Ligne `!.env.example`

Le point d’exclamation `!` inverse une règle précédente. La ligne précédente aurait ignoré `.env.example`; celle-ci dit au contraire que ce fichier doit pouvoir être enregistré dans Git.

Le fichier d’exemple ne contient pas les vrais mots de passe. Il montre seulement les noms des valeurs à fournir. Ainsi, un autre membre de l’équipe sait quoi configurer sans recevoir les secrets.

### Lignes `*.db` et `*.sqlite3`

Elles ignorent les fichiers dont le nom se termine par `.db` ou `.sqlite3`. Dans la démonstration, SQLite stocke la base entière dans un fichier. Ce fichier contient potentiellement les comptes, les consentements et les comptes rendus.

Il ne doit pas être envoyé sur GitHub, pour trois raisons :

1. il contient des données potentiellement personnelles ;
2. plusieurs développeurs auraient des versions incompatibles du même fichier ;
3. le programme peut recréer les tables à partir du code.

### Ligne `server/data/`

Cette ligne ignore le dossier où le serveur place temporairement les enregistrements audio. Un son de réunion est une donnée personnelle particulièrement sensible dans le contexte du projet.

Le fait de l’ignorer protège contre un envoi accidentel sur GitHub, mais cela ne suffit pas à garantir le RGPD. Il faut aussi limiter la durée de conservation, contrôler les accès et supprimer le fichier après traitement. Ces règles sont traitées ailleurs dans le code.

### Ligne `# Node / Vite`

Ce commentaire annonce les règles concernant le frontend. Node.js est le programme qui exécute les outils JavaScript sur l’ordinateur du développeur. Vite est l’outil qui prépare et lance l’interface React pendant le développement.

### Ligne `node_modules/`

`node_modules` contient toutes les bibliothèques téléchargées par `npm install`. Une bibliothèque est du code réutilisable fourni par un autre projet.

Ce dossier peut contenir des dizaines de milliers de fichiers. Il n’est pas envoyé dans Git, car `package.json` et `package-lock.json` permettent de le reconstruire.

### Ligne `dist/`

`dist` signifie généralement « distribution ». C’est le dossier produit lorsque l’on transforme l’interface de développement en fichiers optimisés pour l’hébergement.

Ce résultat peut être recréé avec une commande de construction. Dans ce projet, il est donc ignoré pour éviter de mélanger le code source et le résultat fabriqué.

### Ligne `.vite/`

Vite crée ce dossier pour mémoriser certains calculs et accélérer les démarrages suivants. C’est un cache, c’est-à-dire une copie temporaire destinée à gagner du temps.

Le dossier ne contient pas le code original et peut être supprimé sans perdre le projet.

### Ligne `# OS / IDE`

`OS` signifie « operating system », donc « système d’exploitation », comme Windows ou macOS. `IDE` désigne un logiciel utilisé pour écrire le code, par exemple Visual Studio Code.

### Lignes `.DS_Store` et `Thumbs.db`

macOS crée `.DS_Store` pour mémoriser la présentation d’un dossier. Windows peut créer `Thumbs.db` pour mémoriser les miniatures d’images.

Ces fichiers décrivent l’affichage de l’ordinateur d’un développeur, pas Scribe. Ils sont donc ignorés.

### Lignes `.idea/` et `.vscode/`

Ces dossiers contiennent des préférences créées par certains éditeurs de code. Les ignorer évite d’imposer à toute l’équipe les réglages personnels d’une machine.

Il existe une nuance : une équipe peut décider de partager certains réglages utiles de `.vscode`. Ici, la décision prise est de ne rien partager depuis ce dossier.

### Ligne `*.log`

Un journal, ou « log », est un fichier dans lequel un programme écrit ce qu’il fait et les erreurs rencontrées. L’étoile accepte n’importe quel nom finissant par `.log`.

Les journaux changent à chaque exécution et peuvent contenir des informations techniques ou personnelles. Ils ne doivent pas être versionnés.

### Autres dossiers ignorés

`tmp/pdfs/`, `outputs/` et `tmp/` sont des emplacements de résultats temporaires. `test/`, `preproduction.pdf` et `team-delivery-kit/` correspondent à des éléments locaux que l’équipe ne voulait pas inclure dans ce dépôt final.

Leur présence dans `.gitignore` ne les efface pas du disque. Elle empêche seulement Git de proposer leur ajout.

## 3. Le fichier `pyproject.toml`

Un fichier TOML est un fichier de réglages composé de sections et de paires `nom = valeur`. Les crochets comme `[tool.ruff]` ouvrent une section.

Ruff est un outil qui relit automatiquement le code Python pour repérer des erreurs simples et des incohérences de présentation. Il ne remplace ni les tests ni la relecture humaine.

### Ligne `[tool.ruff]`

Cette ligne ouvre la section de configuration générale de Ruff. Le point dans `tool.ruff` sépare l’idée générale « outil » du nom précis « ruff ».

Tout ce qui suit appartient à cette section jusqu’à la prochaine section entre crochets.

### Ligne `line-length = 100`

Cette ligne fixe à 100 le nombre de caractères recommandé sur une ligne de Python.

`line-length` est le nom du réglage. Le signe `=` associe ce nom à la valeur numérique `100`. Une ligne trop longue est plus difficile à lire sur un petit écran et lors d’une comparaison Git.

Ce n’est pas une règle de fonctionnement de Scribe : changer 100 en 88 ne modifierait pas les résultats du dictaphone. Cela modifierait seulement les alertes de l’outil de qualité.

### Ligne `target-version = "py312"`

Cette ligne annonce que le code vise Python 3.12. Les guillemets indiquent une chaîne de caractères, donc du texte.

Ruff peut alors proposer des règles compatibles avec cette version. Si le serveur réel utilisait une version plus ancienne, certaines écritures acceptées par Ruff pourraient ne pas fonctionner. Le réglage doit donc correspondre à la version réellement installée.

### Ligne `[tool.ruff.lint]`

Cette ligne ouvre la partie consacrée au « lint ». Un linter est un relecteur automatique : il signale un import inutilisé, un nom inconnu ou une écriture inutilement compliquée.

### Ligne `select = ["E", "F", "I", "UP", "B", "SIM"]`

Les crochets forment une liste. Une liste est une suite ordonnée de valeurs. Ici, chaque texte active une famille de contrôles :

- `E` vérifie des règles générales de présentation et certaines erreurs ;
- `F` repère notamment les noms inconnus et les imports inutilisés ;
- `I` vérifie l’ordre des imports ;
- `UP` suggère des écritures Python plus modernes ;
- `B` recherche des erreurs fréquentes ;
- `SIM` suggère des simplifications.

Ces lettres seraient du jargon inutile si on se contentait de les réciter. Leur rôle concret est que la commande `ruff check` sache quelles catégories examiner.

### Ligne `ignore = ["B008"]`

Cette liste demande à Ruff de ne pas signaler la règle portant le numéro `B008`.

Le commentaire après `#` explique pourquoi : FastAPI place parfois un appel servant à fournir une dépendance dans la valeur par défaut d’un paramètre. Ruff considère normalement cette forme comme risquée, mais elle est volontaire dans FastAPI.

Ignorer une règle ne signifie pas que l’erreur est corrigée. Cela signifie que l’équipe accepte précisément ce cas. Une bonne pratique est donc de limiter l’exception à un code précis, comme ici, au lieu de désactiver toute une famille de contrôles.

### Ligne `[tool.pytest.ini_options]`

Cette ligne ouvre les réglages de Pytest. Pytest est un programme qui lance automatiquement des scénarios de vérification écrits en Python.

### Ligne `testpaths = ["server/tests"]`

Cette liste indique à Pytest de chercher les tests dans le dossier `server/tests`.

Elle n’affirme pas que tous les tests existent ni qu’ils réussissent. Elle indique seulement où les trouver lorsqu’on exécute Pytest.

## 4. Le fichier `server/.env.example`

Ce fichier est un formulaire de configuration. La partie à gauche de `=` est le nom attendu par le programme. La partie à droite est une valeur d’exemple ou une valeur par défaut.

Le vrai fichier s’appelle `.env`; il n’est pas envoyé sur GitHub. `.env.example` explique uniquement sa structure.

### `ENVIRONMENT=development`

`ENVIRONMENT` indique le contexte d’exécution. `development` signifie que l’application tourne pour être construite et testée, pas encore comme service public final.

Cette valeur a notamment une conséquence sur le cookie de session : en production, le code demande qu’il soit envoyé uniquement par HTTPS.

### `SECRET_KEY=replace-with-a-long-random-secret`

Cette valeur sert à signer les informations de session. « Signer » signifie produire une preuve mathématique permettant au serveur de détecter si le contenu a été modifié.

La phrase fournie n’est pas un secret sûr. Elle ordonne au développeur de la remplacer par une longue valeur aléatoire. Si l’application publique conservait cette valeur connue, une personne malveillante pourrait tenter de fabriquer de fausses données de session.

Une signature ne chiffre pas forcément le contenu. Le chiffrement cherche à cacher le texte; la signature cherche surtout à prouver qu’il n’a pas été modifié.

### `DATABASE_URL=sqlite:///./scribe.db`

Cette adresse indique comment joindre la base de données. `sqlite` choisit le moteur SQLite. `./scribe.db` désigne un fichier nommé `scribe.db` placé relativement au dossier depuis lequel le serveur est lancé.

SQLite est simple pour une démonstration locale, car il ne nécessite pas de serveur de base de données séparé. En revanche, un fichier local n’est pas adapté à plusieurs serveurs fonctionnant en parallèle ni à un hébergement où le disque peut disparaître après une exécution.

### `CORS_ORIGINS=http://localhost:5174`

CORS est une règle de sécurité appliquée par le navigateur. Elle détermine quelles origines ont le droit d’appeler le backend.

Une origine est la combinaison du protocole, du nom de machine et du port. Ici :

- `http` est le protocole ;
- `localhost` désigne l’ordinateur actuel ;
- `5174` est le port, c’est-à-dire le numéro de la porte utilisée par le frontend.

Cette valeur autorise l’interface locale à appeler l’API. Elle n’ouvre pas le serveur à toutes les adresses.

### `FRONTEND_URL=http://localhost:5174`

Cette valeur indique au backend où se trouve l’interface. Elle sert par exemple à fabriquer un lien de consentement que le destinataire ouvrira dans son navigateur.

### `API_PUBLIC_URL=http://localhost:8000`

Cette valeur est l’adresse publique prévue pour le backend. Le port `8000` est la porte du serveur FastAPI.

Sur l’ordinateur local, `localhost` signifie « cet ordinateur-ci ». Envoyer un lien contenant `localhost` à une autre personne ne lui donne pas accès au premier ordinateur : chez elle, `localhost` désigne son propre ordinateur.

### `UPLOAD_DIR=./data/recordings`

Cette ligne choisit le dossier temporaire des enregistrements audio. Le chemin commence par `./`, ce qui signifie « à partir du dossier courant ».

Le code créera ce dossier s’il n’existe pas. En production, ce stockage local doit être remplacé ou encadré, car il n’est ni partagé entre plusieurs machines ni durable dans certaines offres sans serveur permanent.

### `MAX_AUDIO_MB=50`

Cette valeur limite un fichier audio à 50 mégaoctets. Un mégaoctet est une unité de taille informatique.

La limite protège la mémoire et le disque contre un fichier beaucoup trop grand. Elle ne garantit pas à elle seule que le contenu est réellement un son.

### `RESULT_RETENTION_DAYS=30`

Cette valeur annonce une conservation des résultats pendant 30 jours. Une durée de conservation est nécessaire au titre du principe RGPD de limitation : on ne garde pas une donnée indéfiniment « au cas où ».

Attention : une valeur de configuration ne supprime rien toute seule. Il faut également un mécanisme exécuté régulièrement pour effacer les résultats arrivés à expiration. Si ce mécanisme n’existe pas, la promesse n’est pas réellement appliquée.

### Informations sur le responsable des données

`DATA_CONTROLLER_NAME` contient le nom légal de l’organisation qui décide pourquoi et comment les données sont traitées.

`DATA_CONTROLLER_ADDRESS` contient son adresse postale.

`PRIVACY_CONTACT_EMAIL` contient l’adresse permettant d’exercer les droits relatifs aux données personnelles.

Les valeurs d’exemple doivent être remplacées avant une utilisation réelle. Sinon, l’information fournie aux personnes serait incomplète ou fausse.

### Configuration Mistral

`MISTRAL_API_KEY` reçoit la clé secrète autorisant le serveur à appeler l’API Mistral.

`VOXTRAL_MODEL` choisit le modèle destiné à transformer l’audio en texte. Un modèle est un système entraîné à produire un résultat à partir d’une entrée.

`SUMMARY_MODEL` choisit le modèle destiné à transformer la transcription en compte rendu structuré.

Le texte du nom de modèle n’est pas une preuve que le fournisseur l’acceptera. Il faut vérifier le nom réellement disponible pour le compte, la région, les limites et le tarif dans la documentation et dans une réponse réussie de l’API.

### Configuration Google

`GOOGLE_CLIENT_ID` identifie l’application Scribe auprès de Google.

`GOOGLE_CLIENT_SECRET` prouve au serveur Google que la demande vient bien de cette application. Il ne doit jamais être placé dans le frontend, car tout code envoyé au navigateur peut être lu par l’utilisateur.

OAuth 2.0 est le protocole d’autorisation utilisé. OpenID Connect ajoute une couche d’identité permettant de savoir quel utilisateur s’est connecté. SSO signifie que l’utilisateur réemploie son compte Google au lieu de créer un nouveau mot de passe propre à Scribe.

### Configuration SMTP

SMTP est le protocole utilisé pour transmettre des courriels entre serveurs.

`SMTP_HOST` est le nom du serveur de courrier. `SMTP_PORT=587` choisit sa porte réseau habituelle pour l’envoi authentifié. `SMTP_USERNAME` et `SMTP_PASSWORD` servent à se connecter. `SMTP_FROM_EMAIL` est l’adresse affichée comme expéditeur.

`SMTP_USE_TLS=true` demande une connexion protégée par TLS. TLS chiffre les échanges sur le réseau afin qu’un intermédiaire ne puisse pas lire facilement le mot de passe ou le contenu.

## 5. Le fichier `server/app/config.py`

Ce fichier transforme les textes du `.env` en un objet Python unique appelé `settings`. Le reste du serveur lit cet objet au lieu de rouvrir le fichier partout.

### Ligne `"""Configuration centralisée de Scribe."""`

Les trois guillemets ouvrent et ferment une chaîne de documentation, appelée docstring. Elle décrit le rôle du fichier pour une personne ou un outil de documentation.

Elle ne crée aucun réglage. Elle explique seulement que les réglages sont regroupés ici.

### Ligne `from functools import lru_cache`

`from ... import ...` demande à Python de rendre un élément disponible dans ce fichier.

`functools` est un module fourni avec Python. Un module est un fichier ou un ensemble de fichiers contenant du code réutilisable. `lru_cache` est ici utilisé pour mémoriser le résultat de `get_settings`.

La conséquence est que l’objet de configuration n’est construit qu’une fois par processus. Un processus est une instance du programme en train de fonctionner.

### Ligne `from pathlib import Path`

`pathlib` est un module standard servant à manipuler des chemins de fichiers. `Path` représente un chemin sous forme d’objet plutôt que comme un simple texte.

Cela permet ensuite d’appeler `.resolve()` et `.mkdir()` de manière lisible, compatible avec les conventions de Windows et de Linux.

### Ligne `from pydantic_settings import BaseSettings, SettingsConfigDict`

`pydantic_settings` est une bibliothèque externe installée grâce à `requirements.txt`.

`BaseSettings` est une classe prévue pour lire les variables d’environnement et vérifier leur type. Une classe est un modèle de fabrication d’objets. `SettingsConfigDict` sert à fournir les règles de lecture du fichier `.env`.

### Ligne `class Settings(BaseSettings):`

Cette ligne définit une nouvelle classe nommée `Settings`.

`class` annonce la définition. `Settings` est le nom choisi en PascalCase : chaque mot commence par une majuscule, convention habituelle pour les classes Python. `(BaseSettings)` signifie que `Settings` reprend les capacités de `BaseSettings`. Le deux-points `:` annonce un bloc indenté.

La classe décrit la forme d’une configuration valide. Elle n’est pas encore l’objet contenant les valeurs; cet objet sera créé à la fin du fichier.

### Ligne `model_config = SettingsConfigDict(env_file=".env", extra="ignore")`

Cette ligne crée un attribut de classe appelé `model_config`.

`env_file=".env"` ordonne à Pydantic de lire le fichier `.env`. `extra="ignore"` signifie qu’une variable supplémentaire non déclarée dans la classe sera ignorée au lieu de provoquer une erreur.

L’avantage est qu’un `.env` partagé avec d’autres outils peut contenir plus de valeurs. L’inconvénient est qu’une faute de frappe peut passer inaperçue : écrire `SMTP_HSOT` au lieu de `SMTP_HOST` crée une valeur inconnue qui sera ignorée.

### Comment lire une ligne de réglage

Prenons :

```python
app_name: str = "Scribe"
```

`app_name` est le nom Python de la valeur. Le trait de soulignement entre les mots correspond à la convention `snake_case`, utilisée pour les variables Python.

`: str` est une annotation de type. Elle indique que la valeur attendue est du texte. Une annotation aide Pydantic, l’éditeur et le lecteur, mais Python n’empêche pas toujours seul une mauvaise valeur. Ici, Pydantic réalise réellement une validation lors de la création de `Settings`.

`=` donne la valeur utilisée si aucune variable d’environnement ne la remplace. `"Scribe"` est une chaîne de caractères.

### Les réglages généraux

`environment: str = "development"` distingue le développement de la production. Le code l’utilise plus tard pour renforcer le cookie en production.

`secret_key: str = "change-this-secret-before-production"` définit un secours volontairement explicite. Il permet de démarrer localement, mais il serait dangereux en production parce que tout le monde connaît ce texte.

`database_url: str = "sqlite:///./scribe.db"` choisit le fichier SQLite local par défaut.

`cors_origins`, `frontend_url` et `api_public_url` contiennent les trois adresses expliquées dans `.env.example`.

`token_minutes: int = 60 * 24` utilise une expression plutôt que le nombre `1440`. `60 * 24` signifie 60 minutes multipliées par 24 heures, donc un jour. Cette écriture explique l’intention au lecteur.

`upload_dir` désigne le dossier audio. `max_audio_mb: int = 50` impose un nombre entier. `result_retention_days: int = 30` représente une durée en jours.

`terms_version` et `privacy_version` mémorisent la version des textes juridiques acceptés. L’objectif est de pouvoir prouver quelle version un utilisateur a vue. Dans ce fichier, la date est seulement une chaîne de texte; la preuve complète dépend aussi de ce qui est enregistré en base.

Les trois valeurs `data_controller...` contiennent les coordonnées juridiques expliquées plus haut.

### Les réglages dont la valeur peut être absente

```python
mistral_api_key: str | None = None
```

La barre verticale `|` se lit « ou ». Cette annotation signifie : la valeur est soit du texte (`str`), soit absente (`None`).

`None` est la valeur Python représentant l’absence de valeur. Cela permet au serveur de démarrer sans clé en environnement local, puis de produire une erreur claire lorsqu’une fonctionnalité Mistral est appelée.

Le même principe est utilisé pour les identifiants Google et plusieurs réglages SMTP.

### Ligne `smtp_port: int = 587`

Cette ligne exige un nombre entier. Si `.env` contient le texte `587`, Pydantic le convertit en entier. Si la valeur est impossible à convertir, par exemple `bonjour`, la création de la configuration échoue au démarrage. C’est préférable à une erreur obscure seulement au moment d’envoyer un mail.

### Ligne `smtp_use_tls: bool = True`

`bool` désigne une valeur vraie ou fausse. `True` est le mot Python pour « vrai ».

Pydantic sait convertir une valeur comme `true` lue dans `.env` en booléen Python. Le programme peut alors décider d’activer ou non TLS.

### Lignes `@property` et `def cors_list(self) -> list[str]:`

Le symbole `@` applique un décorateur. Un décorateur est un outil qui change la manière dont une fonction est utilisée. `@property` permet d’écrire `settings.cors_list` comme si c’était une valeur, alors qu’un calcul est exécuté.

`def` commence la définition d’une fonction. `cors_list` est son nom. `self` représente l’objet `Settings` concerné. `-> list[str]` annonce que le résultat est une liste de textes.

Le deux-points ouvre le bloc de la fonction.

### Ligne de retour de `cors_list`

```python
return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]
```

Cette ligne compacte mérite d’être dépliée :

1. `self.cors_origins.split(",")` coupe le texte chaque fois qu’il rencontre une virgule ;
2. `for origin in ...` examine chaque morceau un par un ;
3. `origin.strip()` retire les espaces au début et à la fin ;
4. `if origin.strip()` écarte les morceaux vides ;
5. les crochets construisent la liste finale ;
6. `return` renvoie cette liste au code qui l’a demandée.

Cette propriété permet d’écrire plusieurs adresses autorisées séparées par des virgules dans une seule variable d’environnement.

Exemple : le texte `"http://a.test, http://b.test"` devient la liste `["http://a.test", "http://b.test"]`.

### Propriété `audio_directory`

```python
return Path(self.upload_dir).resolve()
```

`Path(self.upload_dir)` transforme le texte du chemin en objet `Path`. `.resolve()` produit un chemin absolu, c’est-à-dire un chemin complet à partir de la racine du disque.

Cette transformation évite qu’une partie du programme interprète `./data` depuis un dossier différent d’une autre partie. Elle ne crée pas encore le dossier; cette création se trouve dans `main.py`.

### Propriété `google_sso_configured`

```python
return bool(self.google_client_id and self.google_client_secret)
```

L’opérateur `and` exige que les deux valeurs soient présentes. Si l’une manque, l’expression est considérée comme fausse. `bool(...)` convertit clairement le résultat en `True` ou `False`.

Cette propriété ne teste pas que les identifiants sont acceptés par Google. Elle vérifie seulement que les deux champs ne sont pas vides.

### Propriété `smtp_configured`

Elle exige `smtp_host` et `smtp_from_email`. Elle ne vérifie ni le mot de passe, ni la connexion réelle, ni la livraison d’un mail.

Le nom `configured` doit donc être compris comme « réglages minimaux présents », pas comme « service testé et opérationnel ».

### Propriété `legal_configured`

Cette fonction renvoie vrai seulement si le nom et l’adresse du responsable sont remplis et si l’adresse de contact n’est plus la valeur d’exemple.

Les parenthèses permettent d’écrire la condition sur plusieurs lignes. Chaque `and` signifie que toutes les conditions doivent être vraies.

Cette vérification réduit le risque d’afficher des mentions d’exemple, mais elle ne constitue pas un audit juridique. La conformité dépend des textes, des traitements réels, des contrats et de l’organisation complète.

### Ligne `@lru_cache`

Le décorateur `lru_cache` mémorise le résultat de la fonction suivante. Le premier appel crée `Settings`; les appels suivants récupèrent le même objet.

Pourquoi ? Lire et valider le fichier à chaque demande serait inutile. Avoir un seul objet évite aussi que deux parties du même processus utilisent des valeurs différentes.

Conséquence : si le fichier `.env` est modifié pendant que le serveur tourne, l’objet déjà mémorisé ne change pas. Il faut normalement redémarrer le serveur.

### Fonction `get_settings`

```python
def get_settings() -> Settings:
    return Settings()
```

La fonction ne reçoit aucun paramètre. `-> Settings` annonce qu’elle renvoie un objet de la classe `Settings`.

`Settings()` appelle le constructeur de la classe. Un constructeur fabrique une nouvelle instance, c’est-à-dire un objet concret conforme au modèle. Pydantic lit alors l’environnement, convertit les valeurs et vérifie les types.

### Ligne `settings = get_settings()`

Cette ligne appelle immédiatement la fonction et range le résultat dans la variable globale `settings`.

« Globale » signifie que la variable existe au niveau du fichier et peut être importée ailleurs. Les autres modules peuvent écrire `from app.config import settings`.

La conséquence est importante : une configuration invalide empêche le serveur de démarrer, plutôt que de provoquer une erreur beaucoup plus tard.

## 6. Le fichier `server/app/__init__.py`

La présence de `__init__.py` indique que le dossier `app` est un paquet Python, c’est-à-dire un ensemble de modules pouvant être importés sous un nom commun.

La première ligne est une docstring qui décrit brièvement le backend. La seconde :

```python
__version__ = "1.0.0"
```

crée une variable spéciale contenant la version annoncée du paquet. Les doubles traits de soulignement signalent par convention un nom technique réservé au fonctionnement ou aux métadonnées.

Cette valeur n’incrémente rien automatiquement. Si l’équipe publie une nouvelle version, elle doit décider de la mettre à jour ou utiliser un outil qui le fait.

## 7. Le premier `processing.py`

Au moment de ce commit, le traitement audio n’était volontairement pas encore développé.

```python
def process_recording(_: str) -> None:
```

Cette ligne définit la future fonction. Elle reçoit un texte, qui sera l’identifiant d’un enregistrement. Le paramètre s’appelle `_` pour indiquer qu’il n’est pas encore utilisé.

`-> None` signifie que la fonction n’est pas censée renvoyer un résultat.

```python
raise RuntimeError("Le traitement audio n’est pas encore configuré")
```

`raise` déclenche volontairement une erreur. `RuntimeError` est une catégorie générale d’erreur pendant l’exécution.

Pourquoi faire cela au lieu de laisser la fonction vide ? Une fonction vide donnerait l’impression que le traitement a réussi. Ici, l’échec est immédiat et explicite. Ce fichier sera remplacé par le véritable pipeline dans un commit ultérieur.

## 8. Le fichier `requirements.txt`

Chaque ligne nomme une bibliothèque Python et fixe une version avec `==`. Fixer la version aide chaque membre à installer le même code.

`fastapi` fournit le cadre du serveur HTTP et le système de routes.

`uvicorn[standard]` est le programme qui garde le serveur en écoute sur un port et transmet les requêtes à FastAPI. La partie `[standard]` demande des dépendances supplémentaires recommandées.

`sqlmodel` permet de décrire les tables avec des classes Python et de communiquer avec une base SQL.

`pydantic` vérifie et convertit les données. `pydantic-settings` applique cette logique aux réglages.

`email-validator` vérifie la forme générale d’une adresse électronique. Cela ne prouve pas que la boîte existe.

`python-jose[cryptography]` sert à créer ou vérifier certains jetons signés. Un jeton est un petit texte représentant une autorisation ou une identité.

`bcrypt` fournit une fonction de dérivation pour les mots de passe. Elle transforme le mot de passe en empreinte lente à calculer. Une empreinte n’est pas un chiffrement réversible : on vérifie un mot de passe en recalculant, on ne le déchiffre pas.

`python-multipart` permet à FastAPI de recevoir des formulaires et des fichiers envoyés par le navigateur.

`httpx` est un client HTTP : le backend l’utilise pour appeler d’autres serveurs, comme Mistral.

`python-dotenv` sait lire les fichiers `.env`.

`authlib` implémente notamment OAuth 2.0 et OpenID Connect pour la connexion Google.

`itsdangerous` signe des données, notamment pour les sessions utilisées par Starlette.

`pytest` exécute les tests automatiques.

`ruff` relit la qualité du code comme expliqué précédemment.

Une version fixée apporte de la reproductibilité, c’est-à-dire une installation plus semblable entre ordinateurs. Elle impose aussi une maintenance : les corrections de sécurité futures ne seront pas obtenues tant que l’équipe ne met pas volontairement les versions à jour et ne reteste pas.

## 9. Le script `start.ps1`

PowerShell est un langage de commandes présent sur Windows. Ce script automatise l’installation et le démarrage local.

### `$ErrorActionPreference = "Stop"`

En PowerShell, le signe `$` indique une variable. Cette variable spéciale décide du comportement en cas d’erreur.

La valeur `"Stop"` demande d’arrêter le script lorsqu’une commande produit une erreur gérée par PowerShell. Sans cela, le script pourrait continuer et afficher « lancement » alors qu’une étape indispensable a échoué.

### `$projectRoot = $PSScriptRoot`

`$PSScriptRoot` est une valeur fournie par PowerShell : elle contient le dossier dans lequel se trouve le script.

La ligne en fait une variable au nom plus parlant, `$projectRoot`. Le script peut ainsi fonctionner même si l’utilisateur le lance depuis un autre dossier.

### Construction des chemins

```powershell
$serverPath = Join-Path $projectRoot "server"
$webPath = Join-Path $projectRoot "web"
$pythonPath = Join-Path $serverPath ".venv\Scripts\python.exe"
```

`Join-Path` assemble proprement un dossier et un sous-chemin. La première ligne obtient le dossier backend, la deuxième le frontend, la troisième l’exécutable Python de l’environnement virtuel.

Le choix de `Join-Path` évite de fabriquer les chemins par simple collage de textes. Il respecte mieux les séparateurs de Windows.

### Affichage de la préparation

```powershell
Write-Host "Préparation du backend Scribe..." -ForegroundColor Cyan
```

`Write-Host` affiche un message dans le terminal. `-ForegroundColor Cyan` choisit la couleur. Cela ne modifie pas le projet; cela informe l’utilisateur.

### Création conditionnelle de l’environnement Python

```powershell
if (-not (Test-Path $pythonPath)) {
  python -m venv (Join-Path $serverPath ".venv")
}
```

`Test-Path` vérifie si le fichier Python attendu existe. `-not` inverse le résultat. `if` exécute le bloc entre accolades uniquement si la condition est vraie.

Si l’environnement n’existe pas, `python -m venv` demande à Python de créer un environnement virtuel dans `server/.venv`.

Le script suppose que la commande globale `python` existe déjà. Si Python n’est pas installé ou n’est pas dans le chemin système, cette étape échoue.

### Installation des bibliothèques

```powershell
& $pythonPath -m pip install -r (Join-Path $serverPath "requirements.txt")
```

`&` demande à PowerShell d’exécuter le programme dont le chemin est contenu dans la variable.

`-m pip` lance le gestionnaire de paquets avec le Python de l’environnement virtuel. `install -r` lui demande de lire la liste dans `requirements.txt`.

La conséquence est que les dépendances sont installées à chaque lancement. Pip évite généralement de retélécharger une version déjà présente, mais cette étape peut ralentir le démarrage et nécessite parfois Internet.

### Création du `.env`

Le `if` suivant teste l’existence de `server/.env`. S’il manque, `Copy-Item` copie `.env.example` vers `.env`.

Le message jaune rappelle ensuite de remplacer les valeurs importantes.

Le script ne génère pas lui-même un secret sûr et n’insère pas une clé Mistral. Il crée seulement une copie de départ. L’utilisateur doit la configurer sans l’envoyer sur Git.

### Préparation du frontend

`Push-Location $webPath` entre temporairement dans le dossier `web` tout en mémorisant le dossier précédent.

`npm install` télécharge les bibliothèques JavaScript décrites dans `package.json` et verrouillées dans `package-lock.json`.

`Pop-Location` revient au dossier mémorisé. Cette paire évite que les commandes suivantes soient lancées au mauvais endroit.

### Démarrage des deux serveurs

La première commande `Start-Process powershell` ouvre une nouvelle fenêtre PowerShell et lance Uvicorn depuis le dossier backend.

`app.main:app` signifie : charger le module `app/main.py`, puis récupérer la variable `app` qu’il contient.

`--reload` demande de redémarrer automatiquement le backend lorsque le code change. C’est utile en développement, mais ce mode n’est pas destiné à la production.

`--port 8000` choisit le numéro de porte réseau du backend.

La seconde commande ouvre une autre fenêtre, entre dans le dossier frontend et exécute `npm run dev`. Ce script démarre Vite.

### Ouverture du navigateur

`Start-Sleep -Seconds 5` attend cinq secondes. Cette attente donne aux serveurs un peu de temps pour démarrer, mais elle ne prouve pas qu’ils sont prêts.

`Start-Process "http://localhost:5174"` demande à Windows d’ouvrir cette adresse avec le navigateur par défaut.

Le dernier `Write-Host` affiche l’adresse en vert.

## 10. Le second commit : base de données et point de santé

Le message :

```text
feat(api): initialize database and health endpoint
```

`feat` signifie « fonctionnalité ». Le commit apporte maintenant un comportement observable : le serveur peut initialiser sa base et répondre sur `/api/health`.

Un « endpoint », ou point de terminaison, est une combinaison d’adresse et de méthode HTTP. Par exemple `GET /api/health` demande l’état du serveur sans modifier de donnée.

## 11. Le fichier `server/app/db.py`

### Docstring

La première ligne annonce que le fichier gère une base SQLite par SQLModel.

SQLite est le moteur qui range les données dans un fichier. SQLModel est l’outil Python qui relie des objets à des tables SQL.

### `from __future__ import annotations`

Cette ligne demande à Python de différer l’évaluation de certaines annotations de type.

Concrètement, les annotations sont conservées d’une manière qui évite certains problèmes lorsqu’un type n’est pas encore complètement défini. Elle facilite aussi des écritures modernes. Elle doit être placée près du début du fichier parce que Python impose la position des imports `__future__`.

### `from collections.abc import Generator`

`Generator` sert uniquement à décrire le type de la fonction `get_session`.

Un générateur est une fonction qui peut suspendre son exécution avec `yield`, fournir une valeur, puis reprendre plus tard pour effectuer le nettoyage.

### Import SQLModel

```python
from sqlmodel import Session, SQLModel, create_engine
```

`Session` représente une conversation temporaire avec la base. Elle suit les lectures et modifications avant leur validation.

`SQLModel` est la classe de base utilisée pour les modèles de tables.

`create_engine` prépare l’objet qui sait comment se connecter à la base indiquée.

### `from app.config import settings`

Cette ligne récupère l’unique objet de configuration créé dans `config.py`. Ainsi, l’adresse de la base n’est pas répétée dans plusieurs fichiers.

### Ligne `_args = ...`

```python
_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
```

Cette condition écrite sur une seule ligne signifie :

- si l’adresse commence par `sqlite`, créer un dictionnaire contenant `check_same_thread: False`;
- sinon, créer un dictionnaire vide.

Un dictionnaire associe une clé à une valeur. Ici, la clé est `"check_same_thread"` et la valeur est le booléen `False`.

SQLite protège normalement une connexion pour qu’elle ne soit utilisée que depuis le fil d’exécution qui l’a créée. Un fil d’exécution, ou thread, est une suite de travail à l’intérieur d’un programme. FastAPI peut traiter des demandes dans différents threads; ce réglage retire donc ce contrôle.

Cela ne rend pas automatiquement toutes les écritures concurrentes sûres. SQLite conserve des limites lorsque plusieurs opérations veulent écrire en même temps. Cette configuration convient à une démonstration, pas à une forte charge.

Le trait de soulignement au début de `_args` indique par convention que cette variable est interne au module.

### Création de `engine`

```python
engine = create_engine(settings.database_url, echo=False, connect_args=_args)
```

`engine` est l’objet central connaissant l’adresse et la méthode de connexion.

`echo=False` empêche SQLModel d’afficher chaque ordre SQL dans le terminal. Mettre `True` aiderait au débogage, mais pourrait produire beaucoup de texte et exposer des données dans les journaux.

`connect_args=_args` transmet les réglages spéciaux calculés pour SQLite.

Cette ligne prépare le moteur. Elle ne crée pas encore toutes les tables.

### Fonction `init_db`

```python
def init_db() -> None:
    from app import models  # noqa: F401
    SQLModel.metadata.create_all(engine)
```

La fonction ne reçoit rien et ne renvoie rien.

L’import de `models` est placé à l’intérieur pour s’assurer que les classes de tables sont chargées avant `create_all`. Lorsque Python charge ces classes, SQLModel les ajoute à sa liste de métadonnées.

Le commentaire `# noqa: F401` dit à Ruff de ne pas signaler cet import comme inutilisé. Même si le nom `models` n’apparaît pas ensuite, le simple fait de charger le module produit l’effet nécessaire : enregistrer les tables.

`SQLModel.metadata.create_all(engine)` demande de créer toutes les tables manquantes. Cette commande ne remplace pas un système complet de migrations. Une migration est une modification contrôlée de la structure d’une base existante. `create_all` sait créer ce qui manque, mais ne gère pas proprement toutes les transformations futures de colonnes.

### Fonction `get_session`

```python
def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
```

L’annotation `Generator[Session, None, None]` dit que la fonction fournit un objet `Session`. Les deux `None` décrivent des échanges avancés du générateur qui ne sont pas utilisés ici.

`with Session(engine) as session` ouvre une session et garantit sa fermeture lorsque le bloc est terminé, même si une erreur survient.

`yield session` fournit temporairement cette session à FastAPI. Après la fin de la route, l’exécution reprend après `yield`, le bloc `with` se ferme et libère la connexion.

La différence avec `return` est donc importante : `return` terminerait définitivement la fonction; `yield` permet un nettoyage après utilisation.

## 12. Le premier `server/app/main.py`

Ce fichier est le point d’entrée du backend. Uvicorn charge la variable `app` définie ici.

### Import `asynccontextmanager`

Un gestionnaire de contexte encadre une période avec une étape avant et une étape après. La version asynchrone peut coopérer avec un serveur qui traite plusieurs opérations sans bloquer pendant certaines attentes.

Dans cette première version, les opérations sont simples, mais FastAPI recommande ce mécanisme pour la durée de vie de l’application.

### Imports FastAPI et middlewares

`FastAPI` construit l’application.

Un middleware est une couche traversée par une demande avant d’atteindre la route, et par la réponse lors du retour. Il applique une règle commune sans la recopier dans chaque route.

`CORSMiddleware` ajoute les en-têtes que le navigateur utilise pour décider si le frontend est autorisé.

`SessionMiddleware` gère un cookie de session signé. Un cookie est une petite donnée conservée par le navigateur et renvoyée au serveur pour les demandes suivantes.

### Fonction `lifespan`

```python
@asynccontextmanager
async def lifespan(_: FastAPI):
```

Le décorateur transforme cette fonction en gestionnaire de durée de vie. `async def` définit une fonction asynchrone. Le paramètre reçoit l’application FastAPI, mais le nom `_` indique qu’il n’est pas utilisé.

```python
settings.audio_directory.mkdir(parents=True, exist_ok=True)
```

Cette ligne crée le dossier audio.

`parents=True` crée aussi les dossiers parents manquants. `exist_ok=True` évite une erreur si le dossier existe déjà. Cette deuxième propriété rend l’opération idempotente dans ce cas précis : la répéter conduit au même état final « le dossier existe ».

```python
init_db()
```

Cette ligne appelle la fonction qui charge les modèles et crée les tables manquantes.

```python
yield
```

Tout ce qui précède se déroule au démarrage. `yield` rend ensuite le contrôle à FastAPI pour qu’il traite les requêtes. Du code placé après `yield` serait exécuté lors de l’arrêt, mais cette version n’en contient pas.

### Création de l’application

```python
app = FastAPI(title="Scribe API", version="1.0.0", lifespan=lifespan)
```

Cette ligne fabrique l’instance principale.

`title` et `version` apparaissent notamment dans la documentation automatique. `lifespan=lifespan` relie la fonction de démarrage à l’application.

Le premier `app` est le nom de la variable. `FastAPI(...)` appelle le constructeur. Le second `lifespan` à droite du signe `=` est la fonction précédemment définie.

### Middleware de session

`secret_key=settings.secret_key` choisit la clé de signature.

`same_site="lax"` demande au navigateur de limiter certains envois du cookie depuis un autre site. Cela réduit certaines attaques où un site malveillant tente de déclencher une action à la place de l’utilisateur.

`https_only=settings.environment == "production"` calcule un booléen. En production, le cookie est marqué pour n’être transmis que par HTTPS. En développement local HTTP, il reste utilisable.

La sécurité dépend donc de la valeur exacte de `ENVIRONMENT`. Une mauvaise valeur en production pourrait laisser le cookie transmis sur HTTP.

### Middleware CORS

`allow_origins=settings.cors_list` autorise uniquement les origines configurées.

`allow_credentials=True` autorise l’échange de cookies ou d’informations d’authentification. Pour cette raison, on ne devrait pas utiliser une origine universelle `*` avec des données sensibles.

`allow_methods=["GET", "POST", "DELETE"]` limite les méthodes HTTP permises depuis le navigateur. `GET` lit, `POST` crée ou lance une action, `DELETE` demande une suppression.

`allow_headers=["Authorization", "Content-Type"]` permet au frontend d’envoyer ces en-têtes. `Authorization` porte habituellement un jeton d’accès. `Content-Type` indique le format du contenu envoyé.

CORS n’est pas une authentification. Il protège principalement les interactions imposées par le navigateur. Un autre programme peut toujours appeler une API accessible; chaque route sensible doit vérifier l’utilisateur.

### Route de santé

```python
@app.get("/api/health")
def health():
    return {"status": "ok"}
```

Le décorateur relie l’adresse `/api/health` à la fonction `health` pour la méthode GET.

Quand une personne ou un outil demande cette adresse, FastAPI appelle la fonction. La fonction renvoie un dictionnaire Python. FastAPI le transforme en JSON :

```json
{"status": "ok"}
```

JSON est un format texte courant pour échanger des données structurées.

Cette réponse prouve que le processus FastAPI répond et que son démarrage a atteint ce point. Comme `init_db` est exécuté avant l’ouverture du serveur, elle suggère aussi que l’initialisation n’a pas bloqué le démarrage.

Elle ne prouve pas que Mistral, SMTP, Google ou toutes les opérations de base fonctionnent. Un point de santé complet pourrait vérifier ces dépendances avec prudence, sans exposer de secrets.

## 13. Ce que Yanis doit pouvoir résumer à l’oral

« Dans mes deux premiers commits, j’ai séparé les réglages du code afin de ne pas écrire les secrets et les adresses à plusieurs endroits. Pydantic lit le `.env`, convertit les types et fournit un objet `settings` unique. J’ai ensuite créé le moteur SQLModel, une session de base fermée automatiquement, l’initialisation des tables au démarrage, les règles de session et CORS, puis une route `/api/health`. SQLite et le disque local sont adaptés à notre démonstration, mais pas à une architecture serverless répartie sur plusieurs instances; pour la production, il faudra une base et un stockage gérés et partagés. »

## 14. Questions pièges possibles

**Le `.env.example` protège-t-il automatiquement les secrets ?**  
Non. Il montre seulement les noms attendus. La protection vient de l’absence de vraies valeurs dans ce fichier, de `.gitignore`, des contrôles avant commit et du remplacement immédiat de tout secret exposé.

**Pourquoi `settings` est-il créé une seule fois ?**  
Pour éviter de relire et revalider le même fichier à chaque requête et pour fournir des valeurs cohérentes dans tout le processus.

**Pourquoi SQLite a-t-il été choisi ?**  
Pour réduire le nombre de services nécessaires à la démonstration locale. Ce choix est simple, mais il ne convient pas au déploiement final multi-instance.

**Est-ce que `/api/health` garantit que tout marche ?**  
Non. Il garantit seulement que le serveur répond après son initialisation de base.

**CORS empêche-t-il un pirate d’appeler l’API ?**  
Non. CORS est une règle appliquée par les navigateurs. L’authentification et les contrôles d’autorisation restent obligatoires sur le backend.

**Pourquoi utiliser `yield` pour la session ?**  
Parce qu’il faut donner la session à la route puis reprendre la fonction afin de la fermer proprement.

**Pourquoi un nom commence-t-il parfois par `_` ?**  
C’est une convention indiquant « valeur interne » ou « paramètre volontairement inutilisé ». Cela ne rend pas la valeur secrète.

