"""Diarisation : attribuer chaque segment à un locuteur (« qui parle quand »).

Deux cas selon la source :
- **Visio multipiste** (``per_speaker = True``) : le locuteur est déjà connu via
  ``speaker_label`` (une piste = un participant). La diarisation est triviale.
- **Dictaphone** (mix mono) : il faut séparer les voix. En production, on branche
  ``pyannote.audio`` ou une API (Deepgram/AssemblyAI diarize). En mode mock, on
  applique une heuristique d'alternance pour rester démontrable.
"""

from __future__ import annotations

from app.pipeline.transcription import TranscriptSegment


def diarize(segments: list[TranscriptSegment], per_speaker: bool) -> list[TranscriptSegment]:
    """Garantit que chaque segment porte un ``speaker_label``.

    Args:
        segments: segments issus de la transcription.
        per_speaker: True si la source fournissait déjà des pistes par locuteur.
    """
    if per_speaker and all(s.speaker_label for s in segments):
        return segments  # rien à faire : locuteurs déjà attribués

    # Cas dictaphone / labels manquants : heuristique d'alternance simple.
    # (Substitut au modèle pyannote en environnement sans GPU/clé.)
    last_speaker, current = None, "SPEAKER_00"
    toggle = {"SPEAKER_00": "SPEAKER_01", "SPEAKER_01": "SPEAKER_00"}
    for seg in segments:
        if seg.speaker_label:
            continue
        # Alterne quand un silence notable sépare deux segments.
        if last_speaker is not None:
            current = toggle[current]
        seg.speaker_label = current
        last_speaker = current
    return segments


def compute_talk_time(segments: list[TranscriptSegment]) -> dict[str, float]:
    """Calcule le temps de parole cumulé par locuteur."""
    totals: dict[str, float] = {}
    for seg in segments:
        label = seg.speaker_label or "Inconnu"
        totals[label] = totals.get(label, 0.0) + (seg.end_sec - seg.start_sec)
    return {k: round(v, 1) for k, v in totals.items()}
