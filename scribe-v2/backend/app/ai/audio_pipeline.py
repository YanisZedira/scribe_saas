"""Pipeline du **mode dictaphone** (présentiel) — diarisation aveugle + STT.

Chaîne :
    1. PyAnnote Audio 3.1 → diarisation "aveugle" (qui parle quand, sans connaître
       les identités) → segments (start, end, SPEAKER_xx).
    2. Faster-Whisper Large-v3-Turbo → transcription mot-à-mot horodatée.
    3. Alignement : on attribue chaque mot transcrit au locuteur dont l'intervalle
       de diarisation recouvre le timestamp du mot.
    4. Fusion en segments lisibles (un segment par tour de parole).

Les "SPEAKER_00/01" pourront être renommés manuellement dans l'UI (ReportView),
le mapping étant persisté côté base (table SpeakerMap).

Tout est 100 % local (souveraineté) : aucun envoi de l'audio à un tiers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache

from app.ai.faster_whisper_stt import transcribe_file
from app.config import settings


@dataclass
class DiarizedSegment:
    start: float
    end: float
    speaker: str          # étiquette aveugle, ex: "SPEAKER_00"
    text: str = ""


@dataclass
class PipelineResult:
    segments: list[DiarizedSegment]
    speakers: list[str] = field(default_factory=list)
    duration_sec: float = 0.0
    language: str = "fr"


@lru_cache(maxsize=1)
def _get_diarizer():
    """Charge le pipeline PyAnnote (nécessite un token Hugging Face accepté)."""
    from pyannote.audio import Pipeline

    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization-3.1",
        use_auth_token=settings.huggingface_token,
    )
    if settings.whisper_device == "cuda":
        import torch
        pipeline.to(torch.device("cuda"))
    return pipeline


def _assign_speaker(t_start: float, t_end: float,
                    turns: list[tuple[float, float, str]]) -> str:
    """Retourne le locuteur dont l'intervalle recouvre le plus le mot/segment."""
    mid = (t_start + t_end) / 2
    best, best_overlap = "SPEAKER_00", 0.0
    for s, e, spk in turns:
        overlap = max(0.0, min(t_end, e) - max(t_start, s))
        if s <= mid <= e or overlap > best_overlap:
            if overlap >= best_overlap:
                best, best_overlap = spk, overlap
    return best


def _try_diarize(audio_path: str, num_speakers: int | None
                 ) -> list[tuple[float, float, str]] | None:
    """Tente la diarisation PyAnnote. Retourne None si indisponible (mode léger).

    En mode "sans GPU / disque limité", PyAnnote+PyTorch ne sont pas installés :
    on renvoie None et la transcription se fait sans séparation des locuteurs.
    Installer la diarisation : pip install -r requirements-diarization.txt
    """
    if not settings.huggingface_token:
        return None
    try:
        diarizer = _get_diarizer()
    except Exception:  # noqa: BLE001 — pyannote/torch absents ou modèle non accepté
        return None
    diarization = (diarizer(audio_path, num_speakers=num_speakers)
                   if num_speakers else diarizer(audio_path))
    turns = [(t.start, t.end, spk)
             for t, _, spk in diarization.itertracks(yield_label=True)]
    turns.sort(key=lambda x: x[0])
    return turns


def process_recording(audio_path: str, *, language: str | None = "fr",
                      num_speakers: int | None = None) -> PipelineResult:
    """Traite un enregistrement : (diarisation si dispo) + STT + alignement.

    - Si PyAnnote est installé + token HF présent → séparation des locuteurs.
    - Sinon (mode léger) → transcription seule, locuteur unique "Intervenant".
    """
    turns = _try_diarize(audio_path, num_speakers)

    # Transcription mot-à-mot (Faster-Whisper, léger, sans torch) ----------
    stt_segments = transcribe_file(audio_path, language=language,
                                   word_timestamps=True)

    # --- Mode léger : pas de diarisation → un seul locuteur ---------------
    if turns is None:
        segs = [DiarizedSegment(start=s.start, end=s.end,
                                speaker="Intervenant", text=s.text)
                for s in stt_segments if s.text]
        duration = max((s.end for s in segs), default=0.0)
        return PipelineResult(segments=segs, speakers=["Intervenant"],
                              duration_sec=duration, language=language or "fr")

    # 3) Alignement mot → locuteur, regroupé en tours de parole ------------
    merged: list[DiarizedSegment] = []
    for seg in stt_segments:
        words = seg.words or [type("W", (), {"start": seg.start,
                                             "end": seg.end, "text": seg.text})()]
        for w in words:
            spk = _assign_speaker(w.start, w.end, turns)
            if merged and merged[-1].speaker == spk and \
                    w.start - merged[-1].end < 1.5:
                merged[-1].text += w.text
                merged[-1].end = w.end
            else:
                merged.append(DiarizedSegment(start=w.start, end=w.end,
                                             speaker=spk, text=w.text))

    for m in merged:
        m.text = m.text.strip()

    speakers = sorted({m.speaker for m in merged})
    duration = max((m.end for m in merged), default=0.0)
    return PipelineResult(segments=[m for m in merged if m.text],
                          speakers=speakers, duration_sec=duration,
                          language=language or "fr")
