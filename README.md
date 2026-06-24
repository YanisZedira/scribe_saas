# 🎙️ Scribe — Assistant de réunion intelligent (souverain, self-hosted)

Capte une réunion (présentiel, salle visio intégrée, ou bot Teams/Meet/Zoom),
la **transcrit**, identifie **qui parle**, puis génère **compte-rendu, décisions
et actions** — le tout **100 % auto-hébergé** (aucune donnée ne sort de ton infra).

| Transcription | Analyse IA | Visio interne | Bot externe |
|---|---|---|---|
| Faster-Whisper large-v3 (GPU) | Qwen 2.5 (local, Ollama) | LiveKit | Vexa (Teams/Meet/Zoom) |

---

## 🚀 Installation & lancement — UNE SEULE COMMANDE

> **Pré-requis** : une machine **Linux** avec un **GPU NVIDIA** (pilotes installés —
> `nvidia-smi` doit fonctionner) + `git` et `curl`. Sur **Windows**, installe
> d'abord WSL2 + Ubuntu (`wsl --install`) et travaille dans le terminal Ubuntu.
> Tu n'as **rien d'autre** à installer (Docker, GPU toolkit, Python, Node, modèles
> IA : le script s'en charge). **Aucune clé API requise** pour la démo.

Copie-colle ceci dans le terminal :

```bash
git clone https://github.com/YanisZedira/scribe_saas.git && cd scribe_saas/scribe-v2 && sudo bash install.sh
```

Au bout de quelques minutes, ouvre :

- **Application** → http://localhost:3000
- **API / docs** → http://localhost:8000/docs

👉 **Guide détaillé, dépannage et options : [`scribe-v2/README.md`](scribe-v2/README.md)**

---

## 🧪 Les 3 modes de captation

1. **Dictaphone** — réunion en présentiel (micro). *Aucune clé.*
2. **Salle Scribe** — visioconférence intégrée (LiveKit), transcription en direct. *Aucune clé.*
3. **Bot externe** — rejoint **Teams / Google Meet / Zoom** via un lien. *Nécessite une clé Vexa gratuite (sinon mode démo).*

---

## 🗂️ Structure du dépôt

| Dossier | Contenu |
|---|---|
| **`scribe-v2/`** | ⭐ **La version finale** (self-hosted) — c'est ici qu'on installe |
| `scribe-v2/backend/` | API FastAPI + pipeline IA + LiveKit Agent |
| `scribe-v2/frontend/` | Front Next.js (dashboard, salle de réunion, compte-rendu) |
| `scribe-v2/whisper-service/` | Micro-service de transcription GPU (Whisper large-v3) |
| `docs/` | Dossier de cadrage, specs/archi, benchmark, RGPD, business model |
| `benchmark/` | Tableau comparatif des API + scripts de mesure |

---

## 🔒 Souveraineté / RGPD

Tout s'exécute sur ton infrastructure (transcription, LLM, visio). Consentement
bloquant, droit à l'effacement. Pour un client comme Suez : les **mêmes conteneurs**
se déploient on-premise → aucune donnée ne quitte l'entreprise.

## 📄 Licence

Projet pédagogique — RNCP 36146 (Concepteur développeur de solutions digitales).
