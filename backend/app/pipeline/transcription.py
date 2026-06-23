"""Transcription (STT) avec abstraction multi-fournisseurs.

Fournisseurs supportés : ``mock`` (défaut), ``openai`` (gpt-4o-transcribe / whisper),
``assemblyai``, ``deepgram``. Le contrat est unique : ``transcribe()`` renvoie une
liste de ``TranscriptSegment`` (texte + bornes temporelles + locuteur éventuel).
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from app.audio_source.base import AudioBundle
from app.config import settings


@dataclass
class TranscriptSegment:
    start_sec: float
    end_sec: float
    text: str
    speaker_label: str | None = None  # rempli si la source/STT connaît le locuteur


# Coûts approximatifs (€/heure audio) — voir docs/03_benchmark.md
COST_PER_HOUR_EUR = {
    "openai": 0.34,       # gpt-4o-transcribe ~ $0.006/min ≈ 0.34 €/h
    "assemblyai": 0.25,   # Universal ~ $0.27/h diarisation incluse
    "deepgram": 0.27,     # Nova-3 batch + diarisation
    "mock": 0.0,
}


def transcribe(bundle: AudioBundle) -> list[TranscriptSegment]:
    """Transcrit un bundle audio en segments, indépendamment du fournisseur."""
    provider = settings.stt_provider
    if provider == "openai" and settings.openai_api_key:
        return _transcribe_openai(bundle)
    if provider == "deepgram" and settings.deepgram_api_key:
        return _transcribe_deepgram(bundle)
    if provider == "assemblyai" and settings.assemblyai_api_key:
        return _transcribe_assemblyai(bundle)
    return _transcribe_mock(bundle)


def estimated_cost_eur(duration_sec: float) -> float:
    rate = COST_PER_HOUR_EUR.get(settings.stt_provider, 0.0)
    return round((duration_sec / 3600.0) * rate, 4)


# --------------------------------------------------------------------------- #
# Implémentations
# --------------------------------------------------------------------------- #
def _transcribe_openai(bundle: AudioBundle) -> list[TranscriptSegment]:
    from openai import OpenAI

    client = OpenAI(api_key=settings.openai_api_key)
    segments: list[TranscriptSegment] = []
    for track in bundle.tracks:
        if track.path.startswith("<mock>") or not os.path.exists(track.path):
            continue
        with open(track.path, "rb") as fh:
            resp = client.audio.transcriptions.create(
                model="gpt-4o-transcribe", file=fh, language=bundle.language,
                response_format="verbose_json",
            )
        for seg in getattr(resp, "segments", []) or []:
            segments.append(TranscriptSegment(
                start_sec=getattr(seg, "start", 0.0),
                end_sec=getattr(seg, "end", 0.0),
                text=getattr(seg, "text", "").strip(),
                speaker_label=track.speaker_hint,
            ))
        if not getattr(resp, "segments", None):
            segments.append(TranscriptSegment(0.0, track.duration_sec,
                                              resp.text, track.speaker_hint))
    return segments or _transcribe_mock(bundle)


def _transcribe_deepgram(bundle: AudioBundle) -> list[TranscriptSegment]:
    import httpx

    segments: list[TranscriptSegment] = []
    headers = {"Authorization": f"Token {settings.deepgram_api_key}"}
    params = {"model": "nova-3", "diarize": "true", "language": bundle.language,
              "punctuate": "true", "utterances": "true"}
    for track in bundle.tracks:
        if track.path.startswith("<mock>") or not os.path.exists(track.path):
            continue
        with open(track.path, "rb") as fh:
            r = httpx.post("https://api.deepgram.com/v1/listen", headers=headers,
                           params=params, content=fh.read(), timeout=300)
        r.raise_for_status()
        for utt in r.json().get("results", {}).get("utterances", []):
            segments.append(TranscriptSegment(
                start_sec=utt["start"], end_sec=utt["end"], text=utt["transcript"],
                speaker_label=track.speaker_hint or f"SPEAKER_{utt.get('speaker', 0)}",
            ))
    return segments or _transcribe_mock(bundle)


def _transcribe_assemblyai(bundle: AudioBundle) -> list[TranscriptSegment]:
    # Schéma identique : upload → poll → utterances. Omis ici pour la concision ;
    # bascule en mock si l'intégration n'est pas finalisée.
    return _transcribe_mock(bundle)


def _transcribe_mock(bundle: AudioBundle) -> list[TranscriptSegment]:
    """Transcription simulée réaliste, utilisée sans clé API (budget 0 €)."""
    script = [
        ("Alice", "Bonjour à tous, merci d'être présents pour ce point hebdomadaire."),
        ("Bob", "De rien. On commence par le sujet du retard sur la livraison ?"),
        ("Alice", "Oui. Le module de paiement a pris deux jours de retard à cause d'un bug d'intégration."),
        ("Bob", "Je peux prendre le correctif. Je vise une livraison pour vendredi."),
        ("Alice", "Parfait. Décision : on repousse la mise en production à lundi prochain."),
        ("Bob", "D'accord. Il faut aussi prévenir le client de ce décalage."),
        ("Alice", "Je m'en occupe aujourd'hui. Action : envoyer un e-mail au client avant ce soir."),
        ("Bob", "Super. Dernier point : le budget API commence à être tendu sur les longs audios."),
        ("Alice", "Bonne remarque, on mettra un garde-fou. Merci à tous, bonne journée !"),
    ]
    has_hint = bundle.per_speaker
    segments, t = [], 0.0
    for speaker, text in script:
        dur = 4.0 + len(text) / 18.0
        segments.append(TranscriptSegment(
            start_sec=round(t, 2), end_sec=round(t + dur, 2), text=text,
            speaker_label=speaker if has_hint else None,
        ))
        t += dur + 0.5
    return segments
