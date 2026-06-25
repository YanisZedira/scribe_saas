# 🎙️ Scribe — Bot de réunion → Compte-rendu IA (réel, sans fallback)

Un bot **rejoint ta réunion Google Meet / Teams / Zoom**, **écoute et transcrit**
(Vexa), puis **Mistral** génère automatiquement le **résumé**, les **décisions**,
les **prochaines actions** et un **compte-rendu écrit**. Le CR apparaît **tout seul**
à la fin de la réunion (polling automatique).

- **Backend** : FastAPI (`server/`) — Vexa + Mistral, **aucun mode démo**.
- **Frontend** : React + Vite (`web/`) — dashboard, suivi live, compte-rendu.
- **Banc de test** : `test/` — valide Vexa, Voxtral (transcription) et Mistral.

> ⚠️ **Clés API obligatoires** (pas de fausses données) : sans clé, l'app renvoie
> une erreur explicite au lieu d'inventer un résultat.

---

## 1. Configurer les clés — `server/.env`
```bash
cd server
copy .env.example .env     # macOS/Linux : cp .env.example .env
```
Renseigne dans `server/.env` :
```
VEXA_API_KEY=...        # https://vexa.ai/account  (le bot + la transcription)
LLM_API_KEY=...         # https://console.mistral.ai/api-keys  (l'analyse)
```

## 2. Lancer le backend (terminal 1)
```bash
cd server
python -m venv .venv
.venv\Scripts\activate          # macOS/Linux : source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
Vérifie http://localhost:8000/api/health → `vexa_configured` et `llm_configured` à `true`.

## 3. Lancer le frontend (terminal 2)
```bash
cd web
npm install
npm run dev
```
Ouvre **http://localhost:5173**.

---

## 🧪 Tester avec une vraie réunion Google Meet
1. Démarre une réunion sur https://meet.google.com (note le lien `meet.google.com/abc-defg-hij`).
2. Dans Scribe : **Nouvelle réunion** → colle le lien → **Envoyer le bot**.
3. Dans Meet, **admets le participant « Scribe »** (salle d'attente).
4. Parle quelques phrases (décisions, actions à faire…).
5. Quitte/termine la réunion (ou clique **Terminer maintenant**).
6. Le **compte-rendu écrit** s'affiche automatiquement : résumé, décisions,
   prochaines actions, points clés, thèmes — et la transcription complète.

> Astuce : Google Meet est le plus simple pour faire admettre le bot. Pour Teams,
> l'organisateur doit aussi admettre « Scribe ».

---

## Architecture
```
Lien Meet ─► POST /api/meetings ─► Vexa envoie un bot (écoute + transcrit)
Le front interroge GET /api/meetings/{id} toutes les 4 s :
   └─ dès que Vexa indique "terminé" ─► Mistral analyse ─► compte-rendu écrit
                                                              │
                                                        Dashboard
```

## Banc de test (optionnel, pour vérifier chaque brique)
```bash
cd test && pip install -r requirements.txt && copy .env.example .env
python run.py check                 # Vexa + Voxtral + Mistral répondent ?
python run.py pipeline mon_audio.mp3  # Voxtral (transcription) -> Mistral (analyse)
```
