# Commit 2 — `452b4ff` — base SQLModel et FastAPI

[Voir le commit](https://github.com/AshDv/ScribeProject/commit/452b4ff60921cba714272cecdb51713c3d65385a)

Message : `chore(api): add database and health endpoint`.

## `server/app/db.py` — 22 lignes

[Voir le fichier](https://github.com/AshDv/ScribeProject/blob/452b4ff60921cba714272cecdb51713c3d65385a/server/app/db.py#L1-L22)

| Ligne | Code | Explication exacte | Pourquoi / limite |
|---|---|---|---|
| 1 | docstring SQLite/SQLModel | Décrit le module. | La production pourrait ne plus utiliser SQLite ; la docstring serait à mettre à jour. |
| 2 | vide | Sépare docstring/imports. | Style. |
| 3 | `from __future__ import annotations` | Modifie le traitement des annotations du fichier. | Facilite les références de types ; moins indispensable avec les syntaxes modernes utilisées. |
| 4 | vide | Sépare imports futurs et standard. | PEP 8. |
| 5 | `from collections.abc import Generator` | Importe le type abstrait Generator. | Sert à annoter `get_session`. |
| 6 | vide | Sépare standard/externe. | PEP 8. |
| 7 | import SQLModel | Importe session, base des modèles et constructeur de moteur. | Trois responsabilités nécessaires à ce module. |
| 8 | vide | Sépare externe/interne. | PEP 8. |
| 9 | `from app.config import settings` | Récupère l’instance de configuration mise en cache. | Évite une URL codée ici. |
| 10 | vide | Séparation avant valeurs de module. | Lisibilité. |
| 11 | `_args = {...} if ... else {}` | Ternaire Python. Si l’URL commence par `sqlite`, construit un dictionnaire avec `check_same_thread=False`. | `_` marque une variable interne. Ne rend pas SQLite distribuée. |
| 12 | `engine = create_engine(...)` | Construit l’objet moteur partagé. `echo=False` évite le SQL dans la sortie. | Le moteur est une fabrique/gestionnaire de connexions, pas une connexion unique. |
| 13-14 | vides | Deux lignes avant fonction de haut niveau. | PEP 8. |
| 15 | `def init_db() -> None:` | Fonction sans paramètre ni retour utile. | Nom verbe + objet, snake_case. |
| 16 | `from app import models  # noqa: F401` | Import local volontairement « inutilisé ». Il enregistre les classes dans les métadonnées. | `noqa` empêche Ruff F401. Import caché pouvant surprendre. |
| 17 | `SQLModel.metadata.create_all(engine)` | Crée les tables absentes connues. | Ne migre pas un schéma existant ; Alembic requis en production. |
| 18-19 | vides | Séparation. | PEP 8. |
| 20 | signature `get_session` | Générateur produisant `Session`, ne recevant/retournant rien au générateur. | FastAPI l’utilise avec `Depends`. |
| 21 | `with Session(engine) as session:` | Ouvre une session et garantit sa fermeture. | La transaction doit encore être commitée explicitement. |
| 22 | `yield session` | Suspend le générateur et donne la session à la route. | Après la requête, le `with` reprend et ferme. |

### Notions à savoir

- **moteur** : objet SQLAlchemy connaissant l’URL et gérant les connexions ;
- **session** : unité de travail ORM ;
- **métadonnées** : description de toutes les tables ;
- **générateur** : fonction utilisant `yield` ;
- **dependency injection** : FastAPI appelle `get_session` pour la route.

## `server/app/main.py` — 38 lignes dans ce commit

[Voir le fichier](https://github.com/AshDv/ScribeProject/blob/452b4ff60921cba714272cecdb51713c3d65385a/server/app/main.py#L1-L38)

| Ligne | Code | Explication exacte | Pourquoi / limite |
|---|---|---|---|
| 1 | docstring point d’entrée | Indique que Uvicorn charge ce module. | Responsabilité claire. |
| 2 | vide | Séparation. | Style. |
| 3 | import `asynccontextmanager` | Décorateur standard pour un contexte asynchrone basé sur `yield`. | Utilisé par le lifespan. |
| 4 | vide | Sépare imports. | PEP 8. |
| 5 | `from fastapi import FastAPI` | Importe la classe application. | `app` sera une instance. |
| 6 | import `CORSMiddleware` | Couche navigateur cross-origin. | CORS n’est pas une authentification. |
| 7 | import `SessionMiddleware` | Couche de cookie/session signée. | Sert notamment au futur OAuth. |
| 8 | vide | Sépare externe/interne. | PEP 8. |
| 9 | import `settings` | Lit configuration partagée. | Source unique. |
| 10 | import `init_db` | Fonction de création initiale. | Ne fournit pas de migrations. |
| 11-12 | vides | Séparent les fonctions de haut niveau. | PEP 8. |
| 13 | `@asynccontextmanager` | Décore la fonction suivante. | Transforme le générateur en contexte. |
| 14 | `async def lifespan(_: FastAPI):` | Coroutine de cycle de vie. `_` reçoit l’app mais annonce qu’elle n’est pas utilisée. | Annotation FastAPI. |
| 15 | `settings.audio_directory.mkdir(...)` | Crée le dossier et ses parents, sans erreur s’il existe. | Effet de bord au démarrage. |
| 16 | `init_db()` | Crée les tables manquantes. | Rapide pour MVP. |
| 17 | `yield` | Fin de la phase de démarrage ; l’application sert les requêtes. | Rien après `yield`, donc pas de nettoyage d’arrêt. |
| 18-19 | vides | Séparation. | Style. |
| 20 | `app = FastAPI(...)` | Construit l’instance avec titre, version et lifespan. | Uvicorn cible `app.main:app`. |
| 21 | `app.add_middleware(` | Commence l’ajout du middleware session. | Les parenthèses permettent plusieurs lignes. |
| 22 | `SessionMiddleware,` | Premier argument : classe à installer. | La virgule sépare les arguments. |
| 23 | `secret_key=settings.secret_key,` | Clé de signature. | Le défaut doit être remplacé. |
| 24 | `same_site="lax",` | Cookie limité dans plusieurs contextes intersites. | Compromis nécessaire au parcours OAuth. |
| 25 | condition `https_only` | Vrai uniquement si la chaîne vaut exactement `production`. | Une faute dans `ENVIRONMENT` laisserait Secure désactivé. |
| 26 | `)` | Ferme l’appel. | Délimitation syntaxique. |
| 27 | second `app.add_middleware(` | Commence CORS. | L’ordre des middlewares peut compter. |
| 28 | `CORSMiddleware,` | Classe installée. | Contrôle côté navigateur. |
| 29 | `allow_origins=settings.cors_list` | Liste calculée des origines. | Éviter `*` avec credentials. |
| 30 | `allow_credentials=True` | Autorise certains credentials/cookies cross-origin. | Demande une origine explicite. |
| 31 | méthodes GET/POST/DELETE | Préflight autorise seulement ces verbes. | Un futur PUT/PATCH nécessiterait une modification. |
| 32 | en-têtes Authorization/Content-Type | Autorise Bearer et corps JSON/multipart. | Liste minimale. |
| 33 | `)` | Ferme l’appel. | Syntaxe. |
| 34-35 | vides | Deux lignes avant route. | PEP 8. |
| 36 | `@app.get("/api/health")` | Décorateur enregistrant une route GET. | `/api` conserve un espace de noms. |
| 37 | `def health():` | Fonction synchrone sans paramètre. | Nom simple. Une annotation de retour manque. |
| 38 | `return {"status": "ok"}` | Dictionnaire automatiquement sérialisé en JSON. | Prouve seulement que le processus répond. |

## Flux de démarrage

```text
commande Uvicorn
    -> importe app.main
    -> construit app
    -> exécute lifespan avant yield
    -> crée dossier
    -> crée tables
    -> accepte les requêtes
```

## Questions pièges

**`create_all` est-il une migration ?**  
Non. Il crée ce qui manque, mais ne versionne pas les modifications de colonnes.

**Pourquoi `check_same_thread=False` ?**  
Pour permettre l’usage SQLite dans le contexte multithread de FastAPI. Cela ne règle pas la
concurrence multi-instance.

**Health signifie-t-il que Mistral marche ?**  
Non. Il ne teste que FastAPI.

**SessionMiddleware est-il la session SQL ?**  
Non. L’un concerne le cookie Web ; l’autre la transaction de base.

