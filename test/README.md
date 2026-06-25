# 🧪 Banc de test — Vexa + Voxtral + Mistral

Vérifie que la solution fonctionne, brique par brique et en chaîne, **avant** de
brancher un frontend.

- **Voxtral** (Mistral) — transcription audio
- **Mistral** — analyse (résumé, décisions, actions) en JSON
- **Vexa** — bot qui rejoint Teams/Meet/Zoom et transcrit

## Installation

```bash
cd test
python -m venv .venv
.venv\Scripts\activate          # Windows  (macOS/Linux : source .venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env          # puis renseigne MISTRAL_API_KEY et VEXA_API_KEY
```

- `MISTRAL_API_KEY` → https://console.mistral.ai/api-keys (sert à Voxtral ET Mistral)
- `VEXA_API_KEY` → https://vexa.ai/account

## Utilisation

```bash
# 1) Vérifie clés + connexion aux 3 services
python run.py check

# 2) Transcription Voxtral (échantillon de démo si aucun fichier)
python run.py voxtral
python run.py voxtral mon_audio.mp3

# 3) Analyse Mistral (transcription d'exemple si aucun fichier)
python run.py mistral
python run.py mistral ma_transcription.txt

# 4) Chaîne complète sur un fichier audio : Voxtral -> Mistral
python run.py pipeline mon_audio.mp3

# 5) Bot Vexa sur une vraie réunion Teams, puis analyse Mistral
python run.py vexa "https://teams.live.com/meet/1234567890123?p=XYZ"
```

## Conseil de validation
1. `python run.py check` → les 3 doivent afficher ✅.
2. `python run.py pipeline mon_audio.mp3` (enregistre 30 s de voix) → tu vois la
   transcription **puis** l'analyse JSON. C'est le cœur de la solution.
3. `python run.py vexa <lien>` sur une réunion Teams **en cours** → le bot rejoint,
   transcrit, et Mistral analyse à la fin.

> Audio ≤ ~15 min par transcription Voxtral. Pour Teams, commence par Google Meet
> si le bot a du mal à être admis (réglages d'organisateur).
