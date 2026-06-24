"""Moteur STT auto-hébergé : Faster-Whisper (modèle Large-v3-Turbo).

Faster-Whisper (CTranslate2) est 4× plus rapide que le Whisper de référence pour
une qualité équivalente. ``large-v3-turbo`` offre le meilleur compromis
vitesse/qualité pour le multilingue.

Le modèle est chargé une seule fois (singleton) pour éviter de recharger les
poids à chaque requête. GPU (``device="cuda"``, ``compute_type="float16"``) si
disponible, sinon CPU (``int8``).
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

from app.config import settings


@dataclass
class Word:
    start: float
    end: float
    text: str


@dataclass
class STTSegment:
    start: float
    end: float
    text: str
    words: list[Word]


@lru_cache(maxsize=1)
def _get_model():
    """Charge (et met en cache) le modèle Faster-Whisper."""
    from faster_whisper import WhisperModel

    return WhisperModel(
        settings.whisper_model,          # ex: "large-v3-turbo"
        device=settings.whisper_device,  # "cuda" | "cpu"
        compute_type=settings.whisper_compute_type,  # "float16" | "int8"
    )


def transcribe_file(audio_path: str, *, language: str | None = "fr",
                    word_timestamps: bool = True) -> list[STTSegment]:
    """Transcrit un fichier audio complet en segments horodatés.

    Args:
        audio_path: chemin du fichier (wav/mp3/m4a/webm…).
        language: code langue (``None`` = autodétection).
        word_timestamps: nécessaire pour aligner la diarisation (mode physique).
    """
    model = _get_model()
    segments, _info = model.transcribe(
        audio_path,
        language=language,
        word_timestamps=word_timestamps,
        vad_filter=True,  # supprime les silences (gain de coût/temps)
        beam_size=5,
    )
    out: list[STTSegment] = []
    for seg in segments:
        words = [Word(w.start, w.end, w.word) for w in (seg.words or [])]
        out.append(STTSegment(start=seg.start, end=seg.end,
                              text=seg.text.strip(), words=words))
    return out


def transcribe_clip(audio_path: str, *, language: str | None = "fr") -> str:
    """Transcrit un court extrait (ex: une piste LiveKit) → texte simple."""
    model = _get_model()
    segments, _ = model.transcribe(audio_path, language=language, vad_filter=True)
    return " ".join(s.text.strip() for s in segments).strip()
