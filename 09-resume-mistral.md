# Commit 9 — `1f88e83` — résumé structuré Mistral

[Voir le commit](https://github.com/AshDv/ScribeProject/commit/1f88e83fc774214614d25ddcfb07ea9ae989a4f1)

[Voir `llm.py`](https://github.com/AshDv/ScribeProject/blob/1f88e83fc774214614d25ddcfb07ea9ae989a4f1/server/app/llm.py#L1-L166)

## Lignes 1 à 9 — module et imports

| Ligne | Explication |
|---|---|
| 1 | Docstring : intention de fidélité/traçabilité, pas garantie absolue. |
| 2 | Vide. |
| 3 | `json` pour sérialiser le payload. |
| 4 | `Literal` pour fermer certaines valeurs. |
| 5 | Vide entre standard/externe. |
| 6 | `httpx` client HTTP direct, pas SDK Mistral. |
| 7 | Pydantic : modèle, contraintes, erreur de validation. |
| 8 | Vide. |
| 9 | Configuration partagée. |

## `SummaryError`, lignes 12 à 13

Classe PascalCase héritant `RuntimeError`. `pass` fournit un corps vide. Le type permet au pipeline
de capturer précisément les erreurs de résumé.

## `Speaker`, lignes 16 à 20

| Champ | Explication |
|---|---|
| `label: str` | label de diarisation, par exemple speaker_0 |
| `participant_name: str \| None = None` | nom seulement si identifié |
| `confidence: Literal[...]` | valeur obligatoirement `explicit` ou `unknown` |

`confidence` n’est pas une probabilité.

## `KeyPoint`, lignes 22 à 27

- `topic` : sujet ;
- `detail` : développement ;
- `speakers` : labels/noms concernés ;
- `segment_ids` : preuves sources.

Les listes peuvent être vides, car aucun `min_length` n’est posé.

## `Decision`, lignes 29 à 34

- texte de décision ;
- décideurs ;
- justification facultative ;
- segments.

`None` devient `null` en JSON.

## `ActionItem`, lignes 36 à 42

| Ligne | Explication |
|---|---|
| 36 | Classe. |
| 37 | Tâche 1–300 caractères grâce à `Field`. |
| 38 | Responsable facultatif. |
| 39 | Date facultative stockée en texte, sans format ISO imposé. |
| 40 | Priorité facultative limitée à trois mots. |
| 41 | Liste d’IDs. |

## `OpenQuestion`, lignes 44 à 48

Question, responsable facultatif et sources.

## `Risk`, lignes 50 à 55

Risque, mitigation, responsable et sources. Les deux derniers métiers peuvent être `None`.

## `Coverage`, lignes 57 à 69

| Champ | Explication |
|---|---|
| `segment_id` | identifiant unique attendu |
| `classification` | une des sept catégories |
| `used_in` | parties du rapport utilisant le segment |
| `exclusion_reason` | justification si non résumé |

Les catégories sociales/filler/inaudible permettent de couvrir sans polluer le compte rendu.

## `MeetingSummary`, lignes 72 à 82

Objet racine :

| Champ | Contrainte |
|---|---|
| `language` | texte libre |
| `executive_summary` | 1–4 000 caractères |
| `detailed_minutes` | 1–12 000 |
| `speakers` | liste de Speaker |
| `key_points` | liste de KeyPoint |
| `decisions` | liste de Decision |
| `actions` | liste de ActionItem |
| `open_questions` | liste |
| `risks` | liste |
| `coverage` | liste |

Pydantic utilise les annotations pour générer le schéma et valider la sortie.

## `SYSTEM_PROMPT`, lignes 85 à 101

| Ligne/règle | Pourquoi |
|---|---|
| `# Role` | Structure Markdown du prompt. |
| secrétaire méticuleux | Fixe le rôle et l’objectif. |
| `# Rules` | Sépare les contraintes. |
| seulement segments | Interdit source externe/invention. |
| préserver dates/nombres/objections | Évite une synthèse trop lisse. |
| lier chaque extraction | Traçabilité. |
| chaque segment dans coverage | Détection d’oubli. |
| ne pas répéter filler | Lisibilité. |
| action seulement explicite | Évite fausses tâches. |
| owner/due_date null | Empêche de compléter. |
| nom seulement après identification | Évite fausse identité. |
| ne pas exposer e-mails/attributs | Confidentialité. |
| langue dominante | Réponse adaptée. |
| sortie conforme au schema | Parsing robuste. |
| triple guillemet final | Ferme chaîne multiligne. |

Limite prompt injection : une transcription reste une donnée non fiable pouvant contenir des ordres.

## `generate_summary`, lignes 104 à 166

### Signature, lignes 104 à 108

- `transcript: str` ;
- `segments: list[dict]` ;
- `participant_names: list[str]` ;
- sortie `MeetingSummary`.

`list[dict]` est moins précis qu’un modèle `Segment`.

### Clé, lignes 109 à 110

Si absence de clé, lève `SummaryError`. Aucun appel ni coût n’est produit.

### Payload, lignes 112 à 116

Dictionnaire avec participants, transcription complète et segments. Les e-mails ne sont pas
ajoutés explicitement, mais un e-mail prononcé peut rester dans le texte.

### Schéma, ligne 117

`MeetingSummary.model_json_schema()` transforme les classes en contrat JSON Schema.

### Appel, lignes 118 à 145

| Instruction | Explication |
|---|---|
| `try` | Encadre erreurs réseau HTTPX. |
| `response = httpx.post(` | Appel synchrone REST. |
| URL f-string | Base configurable + `/chat/completions`. |
| header Authorization | Bearer clé API. |
| `json={` | HTTPX sérialise le dictionnaire en JSON et pose Content-Type. |
| `model` | Valeur `.env`. |
| `messages` | Tableau system puis user. |
| system content | Prompt constant. |
| user content | Payload sérialisé, accents conservés. |
| `temperature: 0` | Réduit variation. |
| `top_p: 1` | Pas de restriction nucleus supplémentaire. |
| `reasoning_effort: high` | Paramètre demandé ; compatibilité à vérifier. |
| `safe_prompt: True` | Protection fournisseur, non garantie absolue. |
| `response_format` | Demande JSON Schema. |
| `name` | Nom logique `meeting_report`. |
| `schema` | Schéma généré. |
| `strict: True` | Demande respect strict. |
| `timeout=240` | Attente maximale quatre minutes. |

### Erreur transport, lignes 146 à 147

Capture `httpx.HTTPError`, crée une `SummaryError` et conserve la cause avec `from exc`.

### Statut fournisseur, lignes 148 à 149

Une réponse 4xx/5xx n’est pas une exception réseau ; contrôle explicite `>=400`.

### Extraction, lignes 150 à 160

| Instruction | Explication |
|---|---|
| second `try` | Encadre parsing/validation. |
| accès `choices[0].message.content` | Suppose format Chat Completions. |
| `isinstance(content, list)` | Gère une réponse par parties. |
| `"".join(...)` | Concatène textes des dictionnaires de type `text`. |
| `model_validate_json` | Parse JSON puis valide toute la structure. |
| except KeyError/TypeError/ValidationError | Transforme certaines formes invalides. |

Limite : `choices=[]` produit `IndexError`, non capturée.

### Couverture, lignes 162 à 166

| Ligne | Explication |
|---|---|
| 162 | Set des IDs d’entrée. |
| 163 | Liste des IDs retournés dans coverage. |
| 164 | Compare ensembles et longueurs. |
| 165 | Erreur si oubli, invention ou doublon de couverture. |
| 166 | Retourne l’instance validée. |

Le contrôle ne valide pas :

- la fidélité sémantique ;
- les IDs cités dans chaque action ;
- `used_in` ;
- chaque mot ;
- l’unicité des IDs d’entrée.

## Pourquoi appel API direct

`httpx` rend visible le contrat HTTP et évite une dépendance SDK. En contrepartie :

- formats gérés manuellement ;
- évolutions du fournisseur ;
- paramètres potentiellement incompatibles ;
- moins de types.

