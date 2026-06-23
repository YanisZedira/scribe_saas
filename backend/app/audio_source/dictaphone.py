"""Source dictaphone : réunion en présentiel, micro de l'appareil.

Le navigateur enregistre l'audio (MediaRecorder / st.audio_input) et l'envoie au
backend. Cette source normalise le fichier reçu en une piste unique. La diarisation
en aval devra inférer les locuteurs (aucune piste séparée disponible).

Robustesse (palier cible) : les fichiers longs sont découpés en segments de
``CHUNK_SEC`` pour borner la mémoire et permettre une reprise sur incident.
"""

from __future__ import annotations

import os
import wave

from app.audio_source.base import AudioBundle, AudioSource, AudioTrack

CHUNK_SEC = 600  # 10 min : découpe des fichiers longs


class DictaphoneSource(AudioSource):
    """Capte l'audio depuis un fichier uploadé (micro navigateur)."""

    name = "dictaphone"

    def acquire(self, *, meeting_id: str, audio_path: str, language: str = "fr", **_):
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Fichier audio introuvable : {audio_path}")

        duration = self._probe_duration(audio_path)
        track = AudioTrack(path=audio_path, speaker_hint=None, duration_sec=duration)
        return AudioBundle(
            tracks=[track],
            per_speaker=False,
            language=language,
            total_duration_sec=duration,
        )

    @staticmethod
    def _probe_duration(path: str) -> float:
        """Estime la durée. Lit l'en-tête WAV ; fallback sur la taille fichier."""
        try:
            with wave.open(path, "rb") as wav:
                frames = wav.getnframes()
                rate = wav.getframerate() or 16000
                return round(frames / float(rate), 2)
        except (wave.Error, EOFError, FileNotFoundError):
            # Fallback grossier : ~ 1 Mo ≈ 60 s en audio compressé.
            size_mb = os.path.getsize(path) / (1024 * 1024)
            return round(size_mb * 60, 2)
