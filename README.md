# 🎙️ Scribe — Assistant de réunion intelligent

> Captation → Transcription → Diarisation → Classification → Compte-rendu & actions → Tableau de bord

Scribe assiste les réunions **de bout en bout**, dans deux situations d'usage opposées :

- **Mode visio** : l'application héberge / rejoint la visioconférence (plateforme propre **LiveKit**, ou bot sur **Microsoft Teams** / **Google Meet** / **Zoom** via Recall.ai) et récupère l'audio directement.
- **Mode dictaphone** : l'application capte le micro de l'appareil pour les réunions en présentiel.

Les deux modes débouchent sur la **même chaîne de traitement** grâce à une abstraction commune `AudioSource`.

---

## 📦 Contenu du dépôt

| Dossier | Description |
|---|---|
| `backend/` | API **FastAPI** + pipeline IA + workers asynchrones + base de données (la SaaS fonctionnelle) |
| `backend/app/static/` | Front-end SPA (HTML/JS/Tailwind) servi par l'API — tableau de bord, lecteur de réunion |
| `maquette/` | **Maquette Streamlit** (livrable de pré-production) : les deux parcours, écran de consentement, CR placeholder |
| `docs/` | Dossier de cadrage, spécifications & architecture, RGPD, benchmark, business model, choix des modèles |
| `benchmark/` | `benchmark.xlsx` + scripts pytest de mesure de latence des API |
| `.github/workflows/` | CI (lint + tests) |
| `docker-compose.yml` | Stack complète (API + Postgres + Redis + worker) |

---

## 🚀 Démarrage rapide

### Option A — Docker (recommandé)

```bash
cp .env.example .env          # renseignez vos clés API (facultatif : mode mock par défaut)
docker compose up --build
```

- API + front : http://localhost:8000
- Documentation OpenAPI : http://localhost:8000/docs

### Option B — Local (sans Docker)

```bash
cd backend
python -m venv .venv && source .venv/bin/activate      # Windows : .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

La base par défaut est **SQLite** (`scribe.db`), aucune configuration requise. Sans clé API, le pipeline tourne en **mode mock** : tout est fonctionnel de bout en bout avec des données simulées réalistes.

### Maquette Streamlit (livrable pré-prod)

```bash
cd maquette
pip install -r requirements.txt
streamlit run app.py
```

---

## 🔑 Variables d'environnement

Voir `.env.example`. **Tout est optionnel** : chaque brique a un fallback mock pour que l'app tourne sans budget.

| Variable | Rôle | Défaut |
|---|---|---|
| `STT_PROVIDER` | `mock` \| `openai` \| `assemblyai` \| `deepgram` | `mock` |
| `LLM_PROVIDER` | `mock` \| `openai` \| `anthropic` \| `gemini` | `mock` |
| `VISIO_PROVIDER` | `mock` \| `livekit` \| `recall` | `mock` |
| `DATABASE_URL` | Chaîne SQLAlchemy | `sqlite:///./scribe.db` |
| `SECRET_KEY` | Signature JWT | dev key |

---

## 🧱 Architecture (résumé)

```
                    ┌─────────────────────────────────────────┐
   Présentiel  ───► │  AudioSource (abstraction commune)       │
   (dictaphone)     │   ├── DictaphoneSource  (upload/chunks)  │
                    │   ├── LiveKitSource     (plateforme)     │
   Visio       ───► │   └── BotSource         (Teams/Meet/Zoom)│
   (Teams/Meet)     └───────────────┬─────────────────────────┘
                                    │  audio normalisé (wav 16kHz)
                                    ▼
        Transcription → Diarisation → Classification → CR + Actions
              (STT)       (qui parle)   (ton/thèmes)    (JSON structuré)
                                    │
                                    ▼
                       Persistance (Postgres / SQLite)
                                    │
                                    ▼
                       Tableau de bord + API REST
```

Le détail complet est dans [`docs/02_specs_architecture.md`](docs/02_specs_architecture.md).

---

## 📚 Documentation

1. [Dossier de cadrage](docs/01_dossier_cadrage.md) — vision, personae, user stories, roadmap, risques
2. [Spécifications & architecture](docs/02_specs_architecture.md) — C4, ERD, séquences UML, choix d'API
3. [Benchmark des API](docs/03_benchmark.md) — coût / latence / RGPD par famille
4. [RGPD & éthique IA](docs/04_rgpd.md) — consentement, conservation, effacement, DPA
5. [Business model & pricing](docs/05_business_model_pricing.md) — le produit en tant que SaaS commerciale
6. [Choix des modèles & outils](docs/06_choix_modeles_outils.md) — justification technologique

---

## 🧪 Tests

```bash
cd backend
pytest -q                        # tests unitaires (logique non-IA, API mockées)
pytest --cov=app --cov-report=term-missing
```

Mesure de latence des API externes :

```bash
pytest benchmark/scripts/ -q -m latency
```

---

## 📄 Licence

Projet pédagogique — RNCP 36146 (Concepteur développeur de solutions digitales).
