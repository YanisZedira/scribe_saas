# 🎙️ Scribe — Assistant de réunion (Teams → Compte-rendu IA)

Un bot **rejoint ta réunion Teams**, la **transcrit** (via Vexa), puis un **LLM**
la résume, liste les **décisions** et les **actions**, et alimente ton **dashboard**.

- **Backend** : FastAPI (`server/`)
- **Frontend** : React + Vite (`web/`)
- **Transcription** : Vexa (rejoint Teams/Meet/Zoom, STT inclus)
- **Analyse** : LLM compatible OpenAI (Mistral par défaut)
- Pas de Docker, pas de GPU. Deux commandes pour lancer.

---

## 🚀 Lancer l'app

### 1. Backend (terminal 1)
```bash
cd server
python -m venv .venv
.venv\Scripts\activate          # Windows  (macOS/Linux : source .venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env          # (macOS/Linux : cp .env.example .env)
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend (terminal 2)
```bash
cd web
npm install
npm run dev
```

Ouvre **http://localhost:5173** → inscris-toi → **Nouvelle réunion** → colle un lien
Teams → **Envoyer le bot** → à la fin **Terminer & générer le compte-rendu**.

> **Sans clé API**, l'app tourne en **mode démo** (transcription + analyse d'exemple),
> tout le parcours est navigable. Pour le vrai fonctionnement, voir ci-dessous.

---

## 🔑 Clés (pour le mode réel) — dans `server/.env`

| Clé | À quoi ça sert | Où l'obtenir |
|---|---|---|
| `VEXA_API_KEY` | Le bot rejoint Teams **et** transcrit | https://vexa.ai/account (gratuit) |
| `LLM_API_KEY` | Résumé / décisions / actions | https://console.mistral.ai/api-keys |

Après les avoir renseignées, relancer le backend.

---

## 🧱 Fonctionnement

```
Lien Teams ─► POST /api/meetings ─► Vexa envoie un bot
                                         │ (la réunion a lieu)
"Terminer" ─► POST /api/meetings/{id}/finalize
                  ├─ Vexa renvoie la transcription
                  └─ LLM ─► { résumé, décisions, actions, points clés, thèmes }
                                         │
                                   Dashboard utilisateur
```

## 📁 Structure
```
server/   FastAPI  (app/: main, routes, models, auth, vexa, llm, db, config)
web/      React + Vite  (src/: App.jsx, api.js, index.css)
```
