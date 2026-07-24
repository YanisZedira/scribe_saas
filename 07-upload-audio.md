# Commit 7 — `2a1dbd0` — upload audio sécurisé

[Voir le commit](https://github.com/AshDv/ScribeProject/commit/2a1dbd0cc227d07739776329f5f517473913f15c)

Le début de `routes.py` contient l’authentification d’Aymen. La partie fonctionnelle ajoutée par
Yanis commence avec les helpers d’enregistrement.

## Imports nécessaires

- `json` : transforme texte JSON et objets ;
- `Path` : chemin/suppression ;
- `BackgroundTasks` : tâche après réponse ;
- `File`, `Form`, `UploadFile` : multipart ;
- modèles : réunion, participants, enregistrement, liaison, rapport ;
- `process_recording` : contrat de traitement.

## `ALLOWED_AUDIO`

Le dictionnaire associe chaque MIME accepté à l’extension serveur :

```python
{
    "audio/webm": ".webm",
    "audio/wav": ".wav",
    "audio/x-wav": ".wav",
    "audio/mpeg": ".mp3",
    "audio/mp4": ".m4a",
    "audio/x-m4a": ".m4a",
}
```

Une recherche `get(content_type)` répond à deux questions : autorisé et extension.

Limite : MIME fourni par le client, donc non fiable sans inspection des octets.

## `CONSENT_VERSION`

Constante en `UPPER_SNAKE_CASE`. La chaîne fige la preuve associée à l’upload. Elle devrait être
centralisée avec `privacy_version`.

## `owned_recording`, lignes 161 à 166 finales

| Ligne | Explication |
|---|---|
| 161 | Fonction recevant ID, utilisateur et session ; retourne `Recording`. |
| 162 | `session.get` cherche par clé primaire. |
| 163 | Refuse absence ou propriétaire différent. |
| 164 | 404 masque l’existence. |
| 165 | Renvoie l’instance autorisée. |

## `parse_json`, lignes 168 à 169

| Ligne | Explication |
|---|---|
| 168 | Accepte texte ou `None`, annonce une liste. |
| 169 | Ternaire : `json.loads` si valeur, liste vide sinon. |

Limite : JSON corrompu provoque une exception non gérée.

## `recording_detail`, lignes 172 à 208

| Lignes | Explication |
|---|---|
| 172 | Fonction recevant enregistrement et session optionnelle. |
| 173-181 | Expression conditionnelle : requête du rapport seulement si session fournie. |
| 182 | Ouvre dictionnaire `result`. |
| 183 | ID public de l’enregistrement. |
| 184 | Titre. |
| 185 | Enum statut, sérialisée par FastAPI. |
| 186-187 | Dates. |
| 188 | Message d’erreur éventuel. |
| 189 | Transcription. |
| 190 | Segments JSON convertis en liste. |
| 191 | Résumé court. |
| 192-194 | Sujets, décisions, actions convertis. |
| 195 | Version de consentement. |
| 196 | Ferme dictionnaire. |
| 197 | Condition si rapport détaillé. |
| 198 | Ajoute dynamiquement la clé `report`. |
| 199-201 | Modèle, langue, minutes. |
| 202-208 | Chaque JSON détaillé est converti en liste ; ferme le sous-dictionnaire. |
| 209 | Retourne `result`. |

Pourquoi session optionnelle : la création peut appeler la même sérialisation et le détail peut
enrichir avec le rapport.

## `create_recording`, lignes 211 à 262 finales

### Signature

| Ligne/paramètre | Explication |
|---|---|
| décorateur `POST`, 202 | Upload accepté, résultat asynchrone. |
| `async def` | Permet `await audio.read`. |
| `background_tasks` | Injecté par FastAPI. |
| `title: str = Form(...)` | Champ multipart obligatoire, longueur 1–120. |
| `consent: bool = Form(...)` | Confirmation frontend obligatoire. |
| `consent_session_id` | Liaison vers réunion. |
| `audio: UploadFile = File(...)` | Fichier binaire. |
| `user = Depends(current_user)` | JWT obligatoire. |
| `session = Depends(get_session)` | Session SQL. |

### Contrôles, dans l’ordre

| Instruction | Explication / code HTTP |
|---|---|
| `if not consent` | 400 ; confirmation absente. |
| `session.get(ConsentSession, id)` | Charge réunion. |
| absence ou mauvais `owner_id` | 404 ; autorisation. |
| statut différent de RECORDING | 409 ; état incompatible. |
| SELECT participants | Charge source officielle. |
| liste vide ou un retrait | 409 ; tous doivent être actifs. |

L’ordre évite de lire/écrire l’audio avant la validation juridique.

### MIME

```python
content_type = (audio.content_type or "").split(";")[0].lower()
extension = ALLOWED_AUDIO.get(content_type)
```

1. remplace absence par chaîne vide ;
2. retire paramètres après `;` ;
3. normalise minuscules ;
4. cherche l’extension ;
5. 415 si inconnue.

### Taille

```python
data = await audio.read(max_bytes + 1)
```

- lit au plus limite + un octet ;
- chaîne vide de données : 400 ;
- longueur supérieure : 413.

Limite : jusqu’à 50 MiB en RAM par requête.

### Création du fichier et de la base

| Instruction | Explication |
|---|---|
| `mkdir(parents=True, exist_ok=True)` | Garantit le dossier. |
| `recording = Recording(...)` | Construit l’instance ORM. |
| `owner_id=user.id` | Autorisation future. |
| `title=title.strip()` | Retire espaces externes. |
| `original_filename=f"recording{extension}"` | Ne réutilise pas le nom client. Champ mal nommé. |
| `content_type=...` | Conserve le MIME normalisé. |
| `audio_path=""` | Valeur temporaire avant construction de l’ID. |
| `consent_version=...` | Preuve de version. |
| `path = directory / f"{id}{extension}"` | UUID comme nom de stockage. |
| `path.write_bytes(data)` | Écrit les octets sur disque, effet hors transaction. |
| `recording.audio_path = str(path)` | Conserve le chemin. |
| `session.add(recording)` | Prépare INSERT. |
| `session.add(SessionRecording(...))` | Prépare la liaison. |
| `session.commit()` | Valide les deux lignes. |
| `session.refresh(recording)` | Recharge après commit. |
| `background_tasks.add_task(...)` | Planifie le traitement en processus. |
| `return recording_detail(...)` | Réponse 202 avec statut actuel. |

Risques :

- si l’écriture réussit et le commit échoue, fichier orphelin ;
- si le processus meurt après 202, tâche perdue ;
- pas de stockage objet ;
- pas de scan.

## `list_recordings`, lignes 265 à 273

| Ligne | Explication |
|---|---|
| décorateur GET | Lecture de collection privée. |
| signature | JWT et DB injectés. |
| SELECT | Filtre `owner_id`, trie `created_at.desc()`. |
| `.all()` | Matérialise la liste. |
| compréhension | Renvoie seulement ID, titre, statut et date pour chaque ligne. |

Pourquoi vue courte : réduit données et taille du payload.

## `get_recording`, lignes 276 à 282

- ID vient du chemin ;
- utilisateur et DB injectés ;
- `owned_recording` applique l’autorisation ;
- `recording_detail` sérialise.

## `delete_recording`, lignes 285 à 306

| Étape | Explication |
|---|---|
| route DELETE 204 | Succès sans corps. |
| `owned_recording` | Empêche suppression d’autrui. |
| SELECT `SessionRecording` | Recherche liaison unique. |
| `if link: delete` | Supprime si présente. |
| SELECT `StructuredReport` | Recherche rapport. |
| `if report: delete` | Supprime si présent. |
| `Path(...).resolve()` | Chemin absolu. |
| `is_relative_to` + `exists` | Empêche sortie du dossier et erreur d’absence. |
| `unlink()` | Supprime fichier. |
| `session.delete(recording)` | Supprime ligne principale. |
| `session.commit()` | Valide SQL. |

Limite : le fichier est supprimé avant le commit SQL et une tâche active n’est pas annulée.

## Pourquoi « sécurisé » reste relatif

Sécurisé dans ce commit signifie :

- JWT ;
- propriétaire ;
- consentements ;
- liste blanche MIME ;
- taille ;
- nom serveur ;
- chemin contrôlé.

Cela ne signifie pas :

- analyse réelle du format ;
- antivirus ;
- stockage chiffré ;
- durabilité ;
- conformité de production.

