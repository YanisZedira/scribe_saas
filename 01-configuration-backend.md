# Commit 1 — `2646623` — configuration backend

[Voir le commit](https://github.com/AshDv/ScribeProject/commit/2646623fc7c4bf83106cc4629ffa934131303012)

Message : `chore(api): add backend configuration`.

- `chore` : fondation technique, sans fonctionnalité utilisateur complète.
- `api` : périmètre backend.
- `add` : le commit ajoute cette fondation.
- `backend configuration` : responsabilité centrale du diff.

## `.gitignore` — 32 lignes

[Voir le fichier](https://github.com/AshDv/ScribeProject/blob/2646623fc7c4bf83106cc4629ffa934131303012/.gitignore)

| Lignes | Code | Explication littérale | Pourquoi / limite |
|---|---|---|---|
| 1 | `# Python` | Commentaire. `#` rend le reste non exécuté. | Sépare les familles de motifs. |
| 2 | `__pycache__/` | Ignore tous les dossiers portant ce nom. `/` indique un dossier. | Cache Python régénérable. |
| 3 | `*.py[cod]` | `*` accepte tout préfixe ; `[cod]` accepte une lettre parmi c, o, d. | Ignore le bytecode et certaines extensions compilées. |
| 4 | `.venv/` | Ignore le virtualenv local nommé `.venv`. | Contient des dépendances propres à la machine. |
| 5 | `venv/` | Même règle pour un autre nom courant. | Évite un commit massif accidentel. |
| 6 | `*.egg-info/` | Ignore les métadonnées Python générées. | Elles peuvent être reconstruites. |
| 7 | ligne vide | Aucune instruction. | Séparation visuelle. |
| 8 | `# Secrets & DB` | Titre de section. | Signale les fichiers sensibles. |
| 9 | `.env` | Ignore exactement les fichiers nommés `.env`. | Empêche normalement de commiter les vraies clés. |
| 10 | `.env.*` | Ignore les variantes comme `.env.local`. | Plusieurs environnements peuvent contenir des secrets. |
| 11 | `!.env.example` | `!` réautorise le modèle d’exemple. | Le contrat est versionné, pas les valeurs réelles. |
| 12 | `*.db` | Ignore les bases avec extension `.db`. | Elles peuvent contenir comptes et transcriptions. |
| 13 | `*.sqlite3` | Variante d’extension SQLite. | Même justification. |
| 14 | `server/data/` | Ignore le stockage audio local. | Empêche l’envoi de voix dans Git. |
| 15 | vide | Séparation. | Aucun effet. |
| 16 | `# Node / Vite` | Titre. | Regroupe le frontend généré. |
| 17 | `node_modules/` | Ignore les paquets npm téléchargés. | Volumineux et reproductibles avec le lockfile. |
| 18 | `dist/` | Ignore le build Vite. | Artefact généré par `npm run build`. |
| 19 | `.vite/` | Ignore le cache de développement. | Régénérable. |
| 20 | vide | Séparation. | Aucun effet. |
| 21 | `# OS / IDE` | Titre. | Fichiers propres aux outils. |
| 22 | `.DS_Store` | Métadonnée macOS Finder. | Sans intérêt métier. |
| 23 | `Thumbs.db` | Cache de miniatures Windows. | Sans intérêt métier. |
| 24 | `.idea/` | Réglages JetBrains. | Peut différer selon le développeur. |
| 25 | `.vscode/` | Réglages VS Code locaux. | Ce choix ignore aussi d’éventuels réglages partagés utiles. |
| 26 | `*.log` | Ignore les journaux. | Ils peuvent contenir données ou chemins. |
| 27 | `tmp/pdfs/` | Ignore les PDF temporaires. | Artefacts de travail. |
| 28 | `outputs/` | Ignore les sorties locales. | Ne fait pas partie du produit. |
| 29 | `tmp/` | Ignore le temporaire général. | Attention à ne pas y placer un fichier source utile. |
| 30 | `test/` | Ignore un ancien dossier de tests racine. | Le vrai dossier retenu est `server/tests`. Nom assez large. |
| 31 | `preproduction.pdf` | Ignore un ancien document précis. | Nettoyage du dépôt. |
| 32 | `team-delivery-kit/` | Ignore le kit d’intégration. | Outil local, pas code final. |

Point de sécurité : `.gitignore` prévient les nouveaux commits, mais n’efface pas un secret déjà
présent dans l’historique. Une clé exposée doit être révoquée.

## `pyproject.toml` — 10 lignes

[Voir le fichier](https://github.com/AshDv/ScribeProject/blob/2646623fc7c4bf83106cc4629ffa934131303012/pyproject.toml#L1-L10)

| Ligne | Code | Explication |
|---|---|---|
| 1 | `[tool.ruff]` | Ouvre la table TOML de configuration Ruff. |
| 2 | `line-length = 100` | Entier fixant la longueur d’équipe. Ce n’est pas la valeur historique 79 de PEP 8. |
| 3 | `target-version = "py312"` | Chaîne indiquant Python 3.12 à Ruff. |
| 4 | vide | Sépare les tables. |
| 5 | `[tool.ruff.lint]` | Sous-table consacrée au lint. |
| 6 | `select = [...]` | Tableau de familles : style, erreurs, imports, modernisation, bugs et simplification. |
| 7 | `ignore = ["B008"]` | Désactive une règle. Le commentaire explique que `Depends(...)` est volontaire chez FastAPI. |
| 8 | vide | Séparation. |
| 9 | `[tool.pytest.ini_options]` | Configuration Pytest. |
| 10 | `testpaths = ["server/tests"]` | Tableau contenant le dossier où découvrir les tests. |

## `server/.env.example` — 32 lignes

[Voir le fichier](https://github.com/AshDv/ScribeProject/blob/2646623fc7c4bf83106cc4629ffa934131303012/server/.env.example#L1-L32)

| Ligne | Variable | Explication exacte |
|---|---|---|
| 1 | `# Application` | Commentaire de section. |
| 2 | `ENVIRONMENT=development` | Chaîne utilisée pour différencier développement et production. |
| 3 | `SECRET_KEY=...` | Placeholder à remplacer. Sert aux signatures. Une valeur publique est dangereuse. |
| 4 | `DATABASE_URL=sqlite:///./scribe.db` | URL SQLAlchemy : moteur SQLite, fichier relatif `scribe.db`. |
| 5 | `CORS_ORIGINS=http://localhost:5174` | Origine frontend autorisée par le navigateur. |
| 6 | `FRONTEND_URL=http://localhost:5174` | Adresse utilisée dans les redirections et liens. |
| 7 | `API_PUBLIC_URL=http://localhost:8000` | Adresse publique annoncée du backend, notamment callback Google. |
| 8 | `UPLOAD_DIR=./data/recordings` | Chemin relatif de stockage audio temporaire. |
| 9 | `MAX_AUDIO_MB=50` | Texte converti en entier par Pydantic. |
| 10 | `RESULT_RETENTION_DAYS=30` | Durée configurée, pas preuve que la purge est planifiée. |
| 11 | `DATA_CONTROLLER_NAME=...` | Identité juridique à compléter. |
| 12 | `DATA_CONTROLLER_ADDRESS=...` | Adresse du responsable. |
| 13 | `PRIVACY_CONTACT_EMAIL=...` | Contact pour les droits. |
| 14 | vide | Séparation. |
| 15 | commentaire Mistral | Documente que les deux endpoints partagent un compte API. |
| 16 | `MISTRAL_API_KEY=` | Secret vide dans l’exemple. |
| 17 | `VOXTRAL_MODEL=voxtral-mini-latest` | Alias du modèle de transcription. |
| 18 | `SUMMARY_MODEL=mistral-medium-3-5` | Identifiant demandé pour le résumé. Sa disponibilité doit être vérifiée. |
| 19 | vide | Séparation. |
| 20 | commentaire Google | OAuth 2.0 pour l’autorisation, OIDC pour l’identité. |
| 21-22 | commentaire callback | URI exacte à autoriser dans Google Cloud. |
| 23 | `GOOGLE_CLIENT_ID=` | Identifiant d’application, généralement non suffisant comme secret. |
| 24 | `GOOGLE_CLIENT_SECRET=` | Secret strictement backend. |
| 25 | vide | Séparation. |
| 26 | commentaire invitations | Début du bloc SMTP. |
| 27 | `SMTP_HOST=` | Nom du serveur de courrier. |
| 28 | `SMTP_PORT=587` | Port courant de soumission STARTTLS. |
| 29 | `SMTP_USERNAME=` | Compte d’authentification. |
| 30 | `SMTP_PASSWORD=` | Mot de passe d’application, secret. |
| 31 | `SMTP_FROM_EMAIL=` | Adresse visible comme expéditeur. |
| 32 | `SMTP_USE_TLS=true` | Booléen demandant TLS. Ne teste pas réellement le chiffrement. |

Le vrai fichier doit être `server/.env`. Le script démarre Uvicorn depuis `server`, donc le chemin
relatif `.env` de Pydantic correspond à ce fichier.

## `server/app/__init__.py` — 2 lignes

| Ligne | Code | Explication |
|---|---|---|
| 1 | docstring du paquet | Décrit `app`. La mention Vexa est devenue obsolète et devrait être supprimée. |
| 2 | `__version__ = "1.0.0"` | Variable conventionnelle de version du paquet. |

`__init__.py` permet de traiter le dossier comme paquet importable.

## `server/app/config.py` — 74 lignes

[Voir le fichier](https://github.com/AshDv/ScribeProject/blob/2646623fc7c4bf83106cc4629ffa934131303012/server/app/config.py#L1-L74)

| Lignes | Code / nom | Explication littérale |
|---|---|---|
| 1 | docstring | Responsabilité unique : configuration centralisée. |
| 2 | vide | Séparation de la docstring et des imports. |
| 3 | `from functools import lru_cache` | Import nommé d’un décorateur de cache. |
| 4 | `from pathlib import Path` | Import de la classe objet représentant un chemin. |
| 5 | vide | Sépare bibliothèque standard et paquet externe, convention PEP 8. |
| 6 | import Pydantic Settings | `BaseSettings` lit/valide ; `SettingsConfigDict` configure. |
| 7-8 | vides | Deux lignes avant une classe de haut niveau, PEP 8. |
| 9 | `class Settings(BaseSettings):` | Déclare une classe PascalCase héritant de Pydantic. `:` ouvre le bloc indenté. |
| 10 | `model_config = ...` | Attribut de classe. Lit `.env`, ignore les clés supplémentaires. |
| 11 | vide | Sépare la configuration des champs. |
| 12 | `app_name: str = "Scribe"` | Champ texte avec valeur par défaut. |
| 13 | `environment: str = "development"` | Mode courant. Une enum limiterait mieux les valeurs. |
| 14 | `secret_key: str = ...` | Secret par défaut de démonstration, interdit en production. |
| 15 | `database_url: str = ...` | URL de connexion. |
| 16 | `cors_origins: str = ...` | Chaîne brute, ensuite découpée. |
| 17 | `frontend_url: str = ...` | URL de l’interface. |
| 18 | `api_public_url: str = ...` | URL externe du backend. |
| 19 | `token_minutes: int = 60 * 24` | Expression calculée à 1 440 minutes. Plus lisible qu’un nombre magique. |
| 20 | `upload_dir: str = ...` | Chemin stocké initialement en texte. |
| 21 | `max_audio_mb: int = 50` | Limite typée. |
| 22 | `result_retention_days: int = 30` | Durée typée. |
| 23 | `terms_version` | Version des CGU. |
| 24 | `privacy_version` | Version de notice RGPD. |
| 25 | `data_controller_name` | Chaîne vide force la configuration juridique. |
| 26 | `data_controller_address` | Même principe. |
| 27 | `privacy_contact_email` | Placeholder reconnaissable. |
| 28 | vide | Sépare le service IA. |
| 29 | `mistral_api_key: str \| None = None` | Union : secret présent ou absent. |
| 30 | `mistral_base_url` | Base commune des endpoints REST. |
| 31 | `voxtral_model` | Alias STT. |
| 32 | `summary_model` | Modèle du rapport. |
| 33 | vide | Séparation Google. |
| 34 | `google_client_id` | Optionnel pour permettre un démarrage sans SSO. |
| 35 | `google_client_secret` | Optionnel au démarrage, obligatoire pour la route. |
| 36 | vide | Séparation SMTP. |
| 37 | `smtp_host` | Hôte optionnel. |
| 38 | `smtp_port: int = 587` | Conversion et défaut. |
| 39 | `smtp_username` | Identifiant optionnel. |
| 40 | `smtp_password` | Secret optionnel. |
| 41 | `smtp_from_email` | Expéditeur optionnel. |
| 42 | `smtp_use_tls: bool = True` | Booléen de transport. |
| 43 | vide | Sépare champs et méthodes. |
| 44 | `@property` | Décorateur transformant la méthode suivante en attribut calculé. |
| 45 | `def cors_list(self) -> list[str]:` | `self` est l’instance ; sortie liste de textes. |
| 46 | compréhension | Découpe sur virgule, retire espaces et valeurs vides. |
| 47 | vide | Séparation. |
| 48 | `@property` | Même mécanisme. |
| 49 | `def audio_directory...` | Nom exprime un objet chemin, pas une chaîne. |
| 50 | `Path(...).resolve()` | Construit un chemin absolu. Ne garantit pas encore son autorisation. |
| 51 | vide | Séparation. |
| 52-54 | `google_sso_configured` | Vrai seulement si ID et secret sont non vides. `bool` force un booléen. |
| 55 | vide | Séparation. |
| 56-58 | `smtp_configured` | Vérifie seulement hôte et expéditeur, pas le réseau ni le mot de passe. |
| 59 | vide | Séparation. |
| 60-66 | `legal_configured` | Exige nom, adresse et remplacement du contact fictif. Ne remplace pas un audit juridique. |
| 67-68 | vides | Deux lignes avant fonction de haut niveau. |
| 69 | `@lru_cache` | Mémorise le résultat de la fonction sans argument. |
| 70 | `def get_settings() -> Settings:` | Fabrique et annonce une instance Settings. |
| 71 | `return Settings()` | Appelle le constructeur Pydantic. |
| 72-73 | vides | Séparation. |
| 74 | `settings = get_settings()` | Instance partagée importée par les modules. |

## `server/app/processing.py` initial — 5 lignes

| Ligne | Code | Explication |
|---|---|---|
| 1 | docstring | Annonce une étape encore vide. |
| 2-3 | vides | Séparation PEP 8. |
| 4 | `def process_recording(_: str) -> None:` | Contrat futur. `_` indique paramètre non utilisé ; `str` et `None` sont annotations. |
| 5 | `raise RuntimeError(...)` | Échec volontaire, plutôt que simuler un traitement réussi. |

## `server/requirements.txt` — 15 lignes

Chaque ligne suit `nom==version`. `==` verrouille exactement la version.

| Ligne | Paquet | Rôle |
|---|---|---|
| 1 | FastAPI | routes, dépendances, OpenAPI |
| 2 | Uvicorn standard | serveur ASGI |
| 3 | SQLModel | ORM |
| 4 | Pydantic | validation |
| 5 | Pydantic Settings | environnement |
| 6 | email-validator | validation `EmailStr` |
| 7 | python-jose + cryptography | JWT |
| 8 | bcrypt | mots de passe |
| 9 | python-multipart | fichiers et formulaires |
| 10 | HTTPX | appels HTTP et tests |
| 11 | python-dotenv | lecture environnement |
| 12 | Authlib | Google OIDC |
| 13 | itsdangerous | signature de session |
| 14 | Pytest | tests |
| 15 | Ruff | lint |

Limite : outils de développement et dépendances runtime sont mélangés.

## `start.ps1` — 28 lignes

[Voir le fichier](https://github.com/AshDv/ScribeProject/blob/2646623fc7c4bf83106cc4629ffa934131303012/start.ps1#L1-L28)

| Lignes | Code | Explication littérale |
|---|---|---|
| 1 | `$ErrorActionPreference = "Stop"` | Variable spéciale PowerShell. Toute erreur devient bloquante. |
| 2 | `$projectRoot = $PSScriptRoot` | Dossier contenant le script, indépendant du dossier courant. |
| 3 | `$serverPath = Join-Path ...` | Joint proprement le sous-dossier serveur. |
| 4 | `$webPath = ...` | Même principe pour le frontend. |
| 5 | `$pythonPath = ...` | Chemin exact du Python du venv Windows. |
| 6 | vide | Séparation. |
| 7 | `Write-Host ... Cyan` | Message utilisateur coloré, sans effet métier. |
| 8 | `if (-not (Test-Path $pythonPath)) {` | Teste l’absence de l’exécutable. `-not` inverse. |
| 9 | `python -m venv ...` | Demande au Python système de créer l’environnement. |
| 10 | `}` | Ferme le bloc conditionnel. |
| 11 | `& $pythonPath -m pip install -r ...` | `&` exécute un chemin stocké dans une variable. Installe depuis requirements. |
| 12 | `if (-not (Test-Path ... ".env")) {` | Ne copie l’exemple que si le vrai fichier manque. |
| 13 | `Copy-Item ...` | Crée le `.env` local. |
| 14 | `Write-Host ... Yellow` | Avertit que les secrets doivent être configurés. |
| 15 | `}` | Fin du `if`. |
| 16 | vide | Séparation backend/frontend. |
| 17 | message frontend | Affichage seulement. |
| 18 | `Push-Location $webPath` | Empile le dossier courant puis va dans `web`. |
| 19 | `npm install` | Installe les paquets. Le lockfile fixe la résolution. |
| 20 | `Pop-Location` | Revient au dossier précédent. |
| 21 | vide | Séparation. |
| 22 | message de lancement | Affichage. |
| 23 | `Start-Process powershell ... uvicorn` | Ouvre un nouveau PowerShell, va dans server, lance FastAPI port 8000 avec reload. |
| 24 | `Start-Process powershell ... npm run dev` | Ouvre un second processus et lance Vite. |
| 25 | vide | Séparation. |
| 26 | `Start-Sleep -Seconds 5` | Attend arbitrairement cinq secondes. Ce n’est pas un health check. |
| 27 | `Start-Process "http://localhost:5174"` | Demande au système d’ouvrir l’URL dans le navigateur. |
| 28 | message vert | Confirme l’adresse affichée. |

Limites précises :

- script Windows ;
- aucune vérification Node ;
- aucune vérification de port ;
- installations à chaque lancement ;
- serveurs de développement ;
- délai fixe ;
- pas d’arrêt coordonné ;
- aucun HTTPS.

