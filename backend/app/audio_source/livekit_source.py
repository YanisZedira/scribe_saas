"""Source visio « plateforme propre » : LiveKit (WebRTC auto-hébergeable).

Scribe héberge la visioconférence via LiveKit. L'Egress de LiveKit enregistre
chaque participant sur une **piste séparée** : « qui parle » est connu nativement
(``per_speaker = True``), ce qui simplifie énormément la diarisation.

En l'absence de configuration LiveKit (clés/URL), la source bascule en mode mock
et génère des pistes factices afin que la chaîne complète reste démontrable.
"""

from __future__ import annotations

import os

from app.audio_source.base import AudioBundle, AudioSource, AudioTrack
from app.config import settings


class LiveKitSource(AudioSource):
    """Récupère l'audio multipiste d'une room LiveKit hébergée par Scribe."""

    name = "livekit"

    def supports_per_speaker(self) -> bool:
        return True

    def acquire(self, *, meeting_id: str, room: str | None = None,
                language: str = "fr", egress_dir: str | None = None, **_):
        configured = bool(settings.livekit_url and settings.livekit_api_key)

        if configured and egress_dir and os.path.isdir(egress_dir):
            return self._from_egress(egress_dir, language)

        # --- Mode mock : démontre le chemin multipiste sans infra réelle ----
        tracks = [
            AudioTrack(path=f"<mock>/{room or meeting_id}/alice.wav",
                       speaker_hint="Alice", duration_sec=180.0),
            AudioTrack(path=f"<mock>/{room or meeting_id}/bob.wav",
                       speaker_hint="Bob", duration_sec=180.0),
        ]
        return AudioBundle(tracks=tracks, per_speaker=True, language=language,
                           total_duration_sec=180.0)

    @staticmethod
    def _from_egress(egress_dir: str, language: str) -> AudioBundle:
        """Construit le bundle à partir des fichiers déposés par LiveKit Egress.

        Convention : un fichier ``<participant>.wav`` par participant.
        """
        tracks: list[AudioTrack] = []
        max_dur = 0.0
        for fname in sorted(os.listdir(egress_dir)):
            if not fname.lower().endswith((".wav", ".ogg", ".mp4")):
                continue
            speaker = os.path.splitext(fname)[0]
            path = os.path.join(egress_dir, fname)
            dur = os.path.getsize(path) / (1024 * 1024) * 60  # estimation
            max_dur = max(max_dur, dur)
            tracks.append(AudioTrack(path=path, speaker_hint=speaker,
                                     duration_sec=round(dur, 2)))
        return AudioBundle(tracks=tracks, per_speaker=True, language=language,
                           total_duration_sec=round(max_dur, 2))
