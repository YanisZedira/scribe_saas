# 🎙️ Scribe v2 — Assistant de réunion souverain (self-hosted)

Refonte complète, **100 % auto-hébergeable**, aucune donnée ne quitte ton infra.

| Couche | Techno | Rôle |
|---|---|---|
| Front | **Next.js 14** + Tailwind + Shadcn | UI premium, salle de réunion |
| API | **FastAPI** (Python 3.12) + SQLModel | Orchestration, persistance |
| STT | **Faster-Whisper large-v3** (service GPU) | Transcription (qualité max) |
| Diarisation | **PyAnnote 3.1** (optionnel) | « Qui parle » en présentiel |
| Visio interne | **LiveKit** + **LiveKit Agent** | Notre propre salle de réunion |
| Visio externe | **Vexa** | Bot qui rejoint **Teams / Meet / Zoom** |
| LLM | **Qwen 2.5** via **Ollama** | Résumé / actions / thèmes (prompts JSON d'élite) |

```
Présentiel ─ Recorder ─┐
Salle Scribe ─ LiveKit ─┼─► API FastAPI ─► Whisper large-v3 (GPU) ─► Qwen 2.5 ─► CR + actions
Teams/Meet/Zoom ─ Vexa ─┘                         (souverain, local)
```

---

## ✅ Pré-requis (machine du collègue)

- **GPU NVIDIA** (≥ 8 Go VRAM conseillé) + pilotes à jour
- **Docker** + **NVIDIA Container Toolkit** (pour exposer le GPU aux conteneurs)
- ~15 Go de disque libre (modèles Whisper large-v3 + Qwen)

> Vérifier le GPU dans Docker : `docker run --rm --gpus all nvidia/cuda:12.4.1-base-ubuntu22.04 nvidia-smi`

---

## 🚀 Démarrage en UNE commande

```bash
git clone https://github.com/YanisZedira/scribe_saas.git
cd scribe_saas/scribe-v2
cp .env.example .env            # (optionnel) renseigner VEXA_API_KEY pour Teams/Meet
docker compose up --build
```

Puis, une seule fois, télécharger le modèle LLM :

```bash
docker compose exec ollama ollama pull qwen2.5:7b-instruct
```

Accès :
- **App** : http://localhost:3000
- **API / docs** : http://localhost:8000/docs
- **Whisper** : http://localhost:9000/health
- **Santé globale** : http://localhost:8000/api/health

---

## 🧪 Tester les 3 modes

1. **Dictaphone** (présentiel) : nouvelle réunion → Dictaphone → enregistre → transcription large-v3 → **Analyser** (Qwen).
2. **Salle Scribe** (visio propre) : nouvelle réunion → Salle Scribe → la visio LiveKit s'ouvre, l'agent transcrit en direct → **Terminer & générer le CR**.
3. **Bot externe** (Teams/Meet/Zoom) : nécessite **Vexa** (clé cloud dans `.env`, ou Vexa self-host) → colle le lien → le bot rejoint → **Terminer**.

---

## 🔧 Sans Docker (dev manuel)

<details><summary>Backend</summary>

```bash
cd backend && python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# optionnel diarisation : pip install -r requirements-diarization.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```
</details>

<details><summary>Service de transcription GPU</summary>

```bash
cd whisper-service && docker build -t scribe-stt . && \
docker run -d --gpus all -p 9000:9000 -e STT_API_KEY=secret scribe-stt
```
</details>

<details><summary>LiveKit + Agent + Front</summary>

```bash
livekit-server --dev                       # visio
cd backend && python livekit_agent.py dev  # transcription temps réel
cd frontend && npm install && npm run dev   # UI
```
</details>

---

## 🔌 Vexa en 100 % self-host (Teams/Meet/Zoom souverain)

La démo peut utiliser **Vexa Cloud** (clé). Pour du **tout-souverain**, déploie Vexa
chez toi (Docker), puis dans `scribe-v2/.env` :

```
VEXA_API_URL=http://<ip-vexa>:8056
VEXA_API_KEY=<token-créé-côté-vexa>
```

```bash
git clone https://github.com/Vexa-ai/vexa.git && cd vexa && make lite
```

---

## 🤖 Agents / Skills IA (prompts JSON d'élite)

- Analyse complète en une requête : `app/ai/qwen_prompts.py` (`MASTER_SYSTEM`)
  → `titre, resume, points_cles, themes, ton, decisions, actions, risques,
  prochaines_etapes` (schéma strict, zéro hallucination, few-shot).
- Skills ciblés (registre `SKILLS`) : `resume`, `actions`, `themes`, `ton`,
  `decisions`, `risques`, `email_suivi`.
  - `GET /api/skills` liste les skills ; `POST /api/skill` en exécute un
    (ex. générer l'e-mail de suivi).

---

## 🔒 RGPD / souveraineté

- Tout s'exécute sur ton infra (Whisper, Qwen, LiveKit). Aucune donnée ne sort.
- Consentement bloquant, droit à l'effacement (suppression en cascade).
- Pour Suez : même conteneurs déployés on-premise → argument de bout en bout.
