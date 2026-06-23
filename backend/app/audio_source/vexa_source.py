"""Source visio « plateforme externe » via **Vexa** (open-source, self-hostable).

Vexa envoie un bot dans une réunion **Google Meet / Microsoft Teams / Zoom**,
puis fournit une **transcription temps réel par locuteur**. Une seule intégration
couvre les trois plateformes, et tout peut être auto-hébergé (souveraineté RGPD).

Flux réel :
    1. parse l'URL de réunion → (platform, native_meeting_id, passcode)
    2. POST {VEXA_API_URL}/bots → le bot rejoint la réunion
    3. poll GET /transcripts/{platform}/{native_meeting_id} jusqu'à complétion
    4. DELETE /bots/... pour retirer le bot
    5. renvoie un AudioBundle avec ``prebuilt_transcript`` (Vexa a déjà transcrit)

Sans ``VEXA_API_KEY``, la source bascule en mode mock (démo sans infra).

Réf. API : https://docs.vexa.ai/api/bots — https://docs.vexa.ai/api/transcripts
"""

from __future__ import annotations

import re
import time
from urllib.parse import parse_qs, urlparse

import httpx

from app.audio_source.base import AudioBundle, AudioSource, AudioTrack
from app.config import settings


class VexaError(RuntimeError):
    """Erreur d'intégration Vexa (HTTP, parsing d'URL…)."""


class VexaSource(AudioSource):
    """Bot de réunion multi-plateformes via l'API Vexa."""

    name = "vexa"

    def supports_per_speaker(self) -> bool:
        return True  # Vexa attribue les propos par locuteur nativement

    # ------------------------------------------------------------------ #
    # Parsing d'URL → identifiants Vexa
    # ------------------------------------------------------------------ #
    @staticmethod
    def parse_meeting_url(url: str) -> tuple[str, str, str | None]:
        """Extrait (platform, native_meeting_id, passcode) d'une URL de réunion.

        Exemples :
            https://meet.google.com/abc-defg-hij           → google_meet, abc-defg-hij, None
            https://teams.live.com/meet/1234567890123?p=XYZ → teams, 1234567890123, XYZ
            https://us05web.zoom.us/j/12345678901?pwd=...   → zoom, 12345678901, ...
        """
        u = urlparse(url.strip())
        host = (u.hostname or "").lower()
        qs = parse_qs(u.query)

        # Google Meet
        if "meet.google.com" in host:
            code = u.path.strip("/").split("/")[-1]
            if not re.match(r"^[a-z]{3}-[a-z]{4}-[a-z]{3}$", code):
                raise VexaError("Code Google Meet invalide (attendu : abc-defg-hij).")
            return "google_meet", code, None

        # Microsoft Teams (teams.live.com / teams.microsoft.com)
        if "teams." in host:
            m = re.search(r"/meet/(\d+)", u.path) or re.search(r"(\d{10,})", u.path)
            if not m:
                raise VexaError(
                    "Impossible d'extraire l'ID Teams. Utilisez un lien du type "
                    "https://teams.live.com/meet/<ID>?p=<PASSCODE>."
                )
            passcode = (qs.get("p") or qs.get("passcode") or [None])[0]
            return "teams", m.group(1), passcode

        # Zoom
        if "zoom.us" in host:
            m = re.search(r"/j/(\d+)", u.path) or re.search(r"(\d{9,})", u.path)
            if not m:
                raise VexaError("Impossible d'extraire l'ID Zoom (attendu /j/<ID>).")
            passcode = (qs.get("pwd") or [None])[0]
            return "zoom", m.group(1), passcode

        raise VexaError(
            "Plateforme non reconnue. Liens supportés : Google Meet, Microsoft "
            "Teams, Zoom."
        )

    # ------------------------------------------------------------------ #
    # Envoi du bot
    # ------------------------------------------------------------------ #
    def join(self, *, meeting_url: str, language: str = "fr",
             bot_name: str = "Scribe") -> dict:
        """Envoie un bot dans la réunion. Retourne les identifiants Vexa.

        En mode mock (pas de clé), retourne des identifiants factices.
        """
        platform, native_id, passcode = self.parse_meeting_url(meeting_url)

        if not settings.vexa_api_key:
            return {"platform": platform, "native_meeting_id": native_id,
                    "mock": True}

        payload = {
            "platform": platform,
            "native_meeting_id": native_id,
            "language": language,
            "bot_name": bot_name,
            "recording_enabled": True,
            "transcribe_enabled": True,
            "transcription_tier": "realtime",
        }
        if passcode:
            payload["passcode"] = passcode

        resp = httpx.post(f"{settings.vexa_api_url}/bots",
                          headers=self._headers(), json=payload, timeout=30)
        if resp.status_code >= 400:
            raise VexaError(f"Vexa POST /bots a échoué ({resp.status_code}): "
                            f"{resp.text[:200]}")
        return {"platform": platform, "native_meeting_id": native_id,
                "mock": False}

    # ------------------------------------------------------------------ #
    # Récupération de la transcription
    # ------------------------------------------------------------------ #
    def acquire(self, *, meeting_id: str, meeting_url: str | None = None,
                platform: str | None = None, native_meeting_id: str | None = None,
                language: str = "fr", **_):
        # Résout les identifiants (depuis join() ou depuis l'URL).
        if not (platform and native_meeting_id):
            if not meeting_url:
                raise VexaError("URL de réunion manquante pour la source Vexa.")
            platform, native_meeting_id, _ = self.parse_meeting_url(meeting_url)

        if not settings.vexa_api_key:
            return self._mock_bundle(language)

        segments = self._poll_transcript(platform, native_meeting_id)
        self._stop_bot(platform, native_meeting_id)

        prebuilt = [
            {
                "start_sec": float(s.get("start_time") or 0.0),
                "end_sec": float(s.get("end_time") or 0.0),
                "text": (s.get("text") or "").strip(),
                "speaker_label": s.get("speaker") or "Intervenant",
            }
            for s in segments if (s.get("text") or "").strip()
        ]
        total = max((p["end_sec"] for p in prebuilt), default=0.0)
        return AudioBundle(
            tracks=[AudioTrack(path=f"<vexa>/{platform}/{native_meeting_id}",
                               duration_sec=total)],
            per_speaker=True, language=language, total_duration_sec=total,
            prebuilt_transcript=prebuilt or None,
        )

    # ------------------------------------------------------------------ #
    # Internes
    # ------------------------------------------------------------------ #
    def _headers(self) -> dict:
        return {"X-API-Key": settings.vexa_api_key, "Content-Type": "application/json"}

    def _poll_transcript(self, platform: str, native_id: str) -> list[dict]:
        """Interroge Vexa jusqu'à ce que la réunion soit terminée."""
        url = f"{settings.vexa_api_url}/transcripts/{platform}/{native_id}"
        deadline = time.time() + settings.vexa_poll_timeout_sec
        last_segments: list[dict] = []
        while time.time() < deadline:
            resp = httpx.get(url, headers=self._headers(), timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                last_segments = data.get("segments", []) or last_segments
                if data.get("status") in {"completed", "failed", "stopped"}:
                    break
            time.sleep(settings.vexa_poll_interval_sec)
        return last_segments

    def _stop_bot(self, platform: str, native_id: str) -> None:
        try:
            httpx.delete(f"{settings.vexa_api_url}/bots/{platform}/{native_id}",
                         headers=self._headers(), timeout=15)
        except httpx.HTTPError:
            pass  # le bot s'arrête de toute façon en fin de réunion

    @staticmethod
    def _mock_bundle(language: str) -> AudioBundle:
        """Transcription simulée (per-speaker) pour la démo sans clé Vexa."""
        script = [
            ("Camille", "Bonjour à tous, on démarre le point produit hebdomadaire."),
            ("Aymen", "Salut. Premier sujet : le retard sur l'intégration paiement."),
            ("Camille", "Oui, deux jours de retard à cause d'un bug d'intégration."),
            ("Aymen", "Je prends le correctif, livraison visée pour vendredi."),
            ("Camille", "Décision : on repousse la mise en production à lundi."),
            ("Aymen", "Il faut prévenir le client du décalage."),
            ("Camille", "Action : j'envoie un e-mail au client avant ce soir."),
            ("Aymen", "Dernier point : surveiller le budget API sur les longs audios."),
        ]
        prebuilt, t = [], 0.0
        for speaker, text in script:
            dur = 4.0 + len(text) / 18.0
            prebuilt.append({"start_sec": round(t, 2), "end_sec": round(t + dur, 2),
                             "text": text, "speaker_label": speaker})
            t += dur + 0.4
        return AudioBundle(
            tracks=[AudioTrack(path="<vexa-mock>", duration_sec=t)],
            per_speaker=True, language=language, total_duration_sec=t,
            prebuilt_transcript=prebuilt,
        )
