# Scribe — Choix des modèles & outils (justification de A à Z)

> Décisions techniques tranchées en pré-production. Toute décision non tranchée ici devient une dette en production.

---

## 1. Modèles d'IA

### 1.1 Transcription (STT)

| Palier | Modèle retenu | Pourquoi |
|---|---|---|
| 🟢 Socle | **OpenAI gpt-4o-transcribe** | Une seule clé, multilingue, ~0,34 €/h, JSON verbeux avec timestamps, mise en place en minutes |
| 🔵 Cible | **Deepgram Nova-3** | Diarisation **native** peu chère, batch rapide, bon FR |
| 🟣 Avancé | **Whisper (large-v3) + pyannote.audio** self-host | Souveraineté UE, coût marginal ~0, contrôle total, pas de DPA tiers |

**Décision** : démarrer managé (OpenAI), prévoir la bascule self-host pour le volume et le RGPD. Le code rend ce choix paramétrable (`STT_PROVIDER`).

### 1.2 Diarisation (« qui parle »)

- **Visio multipiste** → triviale (1 piste = 1 personne). Privilégiée car la plus fiable.
- **Dictaphone** → `pyannote.audio` (palier cible/avancé) ; en démo, heuristique d'alternance.
- **Identification nominative** (avancé) → enrôlement vocal optionnel + consentement art. 9.

### 1.3 LLM (résumé, classification, extraction d'actions)

| Palier | Modèle | Pourquoi |
|---|---|---|
| 🟢/🔵 | **GPT-4o-mini** | Meilleur rapport qualité/prix (0,15/0,60 $/1M), `json_object` natif, bon FR |
| 🟣 repli | **Claude Haiku** | Qualité de rédaction, robustesse, diversification fournisseur |

**Sortie structurée** : on impose un schéma JSON (résumé, décisions, actions{description, assignee, due_date}) pour fiabiliser l'extraction et éviter le texte libre non exploitable.

### 1.4 Classification

- **Socle/cible** : LLM (mutualisé avec le CR) → ton, thèmes, urgence.
- **Avancé** : **CamemBERT** fine-tuné (FR) comparé au LLM (accuracy, F1, latence, coût) → recommandation argumentée.

---

## 2. Plateformes de captation visio

| Usage | Outil | Pourquoi |
|---|---|---|
| Plateforme propre | **LiveKit** | Open-source, self-host UE, **Egress multipiste**, WebRTC moderne |
| Teams / Meet / Zoom | **Recall.ai** | **1 intégration = 3 plateformes**, webhooks, pas de frais fixes (0,50 $/h) |
| Repli low-cost | **Jitsi** | Gratuit, self-host |
| ❌ Écarté | Twilio Video | **Fin de vie (EOL)** |

---

## 3. Stack logicielle

| Couche | Choix | Alternative écartée | Raison |
|---|---|---|---|
| Langage | **Python 3.12** | — | Écosystème IA, demandé par le sujet |
| API | **FastAPI** | Flask/Django | Async, OpenAPI auto, typage Pydantic |
| ORM | **SQLModel** | SQLAlchemy nu | Modèles + schémas unifiés et typés |
| Validation | **Pydantic v2** | — | (Dé)sérialisation robuste |
| BDD | **PostgreSQL** (prod) / **SQLite** (dev) | MongoDB | Relationnel adapté (réunions/segments/actions), simple en dev |
| File de tâches | **Redis + RQ** | Celery | Plus simple, suffisant ; fallback BackgroundTasks |
| HTTP client | **httpx** | requests | Async + timeouts |
| Auth | **JWT (jose) + bcrypt (passlib)** | sessions | Stateless, standard SaaS |
| Front | **SPA HTML/JS + Tailwind (CDN)** | React build | Zéro étape de build, tourne immédiatement ; React possible plus tard |
| Maquette | **Streamlit** | — | Demandé par le sujet, idéal pour figer le parcours |
| Lint | **ruff** | flake8+isort+black | Tout-en-un, ultra rapide, PEP 8 |
| Tests | **pytest + respx + coverage** | unittest | Fixtures, mock HTTP, couverture |
| Conteneurs | **Docker + docker-compose** | — | Repro, multi-services |
| CI | **GitHub Actions** | — | Intégré au repo, lint+tests sur PR |
| Déploiement | **Railway / Render** (cible) | — | Semi-auto, simple, pas cher |
| Diagrammes | **Mermaid + PlantUML** | — | Versionnables, demandés (draw.io/PlantUML) |

---

## 4. Principe d'architecture directeur

> **Tout ce qui est externe et susceptible de changer (STT, LLM, visio) est derrière une abstraction interchangeable.**

- `audio_source/` → `AudioSource` (dictaphone / livekit / bot)
- `pipeline/transcription.py` → `STT_PROVIDER`
- `pipeline/llm.py` → `LLM_PROVIDER`

Conséquences : pas de lock-in, tests faciles (mock), bascule managé ↔ self-host par variable d'environnement, résilience (fallback provider).

---

## 5. Stratégie de tests & qualité

- **TDD/BDD** sur la logique non-IA (factory, diarisation, parsing dates, garde-fous RGPD).
- **Mock des API** (respx) → tests rapides, déterministes, sans coût.
- **Couverture ≥ 70 %** des fonctions critiques (socle) ; tests d'intégration de bout en bout (avancé).
- **CI bloquante** : lint + tests + seuil de couverture sur chaque PR.

---

## 6. Décisions tranchées (anti-dette)

| Question | Décision |
|---|---|
| Monolithe ou microservices ? | **API + worker** (modulaire), pas de microservices prématurés |
| Sync ou async ? | **Async** (queue) dès la cible ; sync acceptable pour réunions courtes au socle |
| SQL ou NoSQL ? | **SQL** (relationnel naturel) |
| Managé ou self-host ? | **Managé par défaut**, **self-host disponible** (RGPD/volume) |
| Une intégration visio par plateforme ? | **Non** : Recall.ai mutualise Teams/Meet/Zoom |
| Stockage de l'audio brut ? | **Supprimé après transcription** par défaut (minimisation RGPD) |
