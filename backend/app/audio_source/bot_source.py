"""Source visio « plateforme externe » : bot de réunion via Recall.ai.

Permet à Scribe de rejoindre une réunion **Microsoft Teams**, **Google Meet** ou
**Zoom** sous forme de participant-bot, puis de récupérer l'enregistrement et la
transcription. Une seule intégration (Recall.ai) couvre les trois plateformes,
ce qui évite de maintenir trois SDK propriétaires distincts.

Flux réel :
    1. ``POST /bot`` chez Recall.ai avec l'URL de la réunion → le bot rejoint.
    2. Recall.ai notifie Scribe par webhook quand l'enregistrement est prêt.
    3. Scribe télécharge l'audio (mix ou multipiste selon le plan).

Sans clé ``RECALL_API_KEY``, la source fonctionne en mode mock.
"""

from __future__ import annotations

import httpx

from app.audio_source.base import AudioBundle, AudioSource, AudioTrack
from app.config import settings

_RECALL_BASE = "https://api.recall.ai/api/v1"


class BotSource(AudioSource):
    """Bot multi-plateformes (Teams / Meet / Zoom) via Recall.ai."""

    name = "recall"

    def supports_per_speaker(self) -> bool:
        # Recall fournit des transcriptions diarisées par participant.
        return True

    def join(self, *, meeting_url: str, bot_name: str = "Scribe") -> str:
        """Envoie un bot dans la réunion. Retourne l'identifiant du bot.

        En mode mock (pas de clé), retourne un identifiant factice.
        """
        if not settings.recall_api_key:
            return f"mock-bot-{abs(hash(meeting_url)) % 10_000}"

        resp = httpx.post(
            f"{_RECALL_BASE}/bot",
            headers={"Authorization": f"Token {settings.recall_api_key}"},
            json={"meeting_url": meeting_url, "bot_name": bot_name},
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()["id"]

    def acquire(self, *, meeting_id: str, bot_id: str | None = None,
                language: str = "fr", **_):
        if not settings.recall_api_key or not bot_id or bot_id.startswith("mock-"):
            return self._mock_bundle(language)

        # Récupère les médias produits par le bot une fois la réunion terminée.
        resp = httpx.get(
            f"{_RECALL_BASE}/bot/{bot_id}",
            headers={"Authorization": f"Token {settings.recall_api_key}"},
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        audio_url = (data.get("recordings") or [{}])[0].get("media_url")
        if not audio_url:
            return self._mock_bundle(language)

        local = f"/tmp/{meeting_id}.mp4"
        with httpx.stream("GET", audio_url, timeout=120) as r:
            with open(local, "wb") as fh:
                for chunk in r.iter_bytes():
                    fh.write(chunk)
        track = AudioTrack(path=local, speaker_hint=None, duration_sec=0.0)
        return AudioBundle(tracks=[track], per_speaker=True, language=language)

    @staticmethod
    def _mock_bundle(language: str) -> AudioBundle:
        track = AudioTrack(path="<mock>/recall/mix.wav", duration_sec=240.0)
        return AudioBundle(tracks=[track], per_speaker=True, language=language,
                           total_duration_sec=240.0)
