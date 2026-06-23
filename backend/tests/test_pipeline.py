"""Tests unitaires de la chaîne de traitement (logique non-IA, mode mock)."""

from __future__ import annotations

from app.audio_source.base import AudioBundle, AudioTrack
from app.audio_source.dictaphone import DictaphoneSource
from app.audio_source.factory import get_audio_source
from app.models import CaptureMode
from app.pipeline import classification, diarization, summary, transcription


def _bundle(per_speaker: bool) -> AudioBundle:
    return AudioBundle(tracks=[AudioTrack(path="<mock>/a.wav", duration_sec=60)],
                       per_speaker=per_speaker, total_duration_sec=60)


def test_factory_selects_correct_source():
    assert get_audio_source(CaptureMode.DICTAPHONE).name == "dictaphone"
    assert get_audio_source(CaptureMode.VISIO, "teams").name == "recall"
    assert get_audio_source(CaptureMode.VISIO, None).name == "livekit"


def test_dictaphone_source_is_not_per_speaker():
    assert DictaphoneSource().supports_per_speaker() is False


def test_transcription_mock_produces_segments():
    segs = transcription.transcribe(_bundle(False))
    assert len(segs) > 0
    assert all(s.end_sec >= s.start_sec for s in segs)


def test_diarization_assigns_speaker_to_every_segment():
    segs = transcription.transcribe(_bundle(False))  # dictaphone : pas de hint
    segs = diarization.diarize(segs, per_speaker=False)
    assert all(s.speaker_label for s in segs)


def test_diarization_keeps_known_speakers_in_visio():
    segs = transcription.transcribe(_bundle(True))  # visio : hints présents
    segs = diarization.diarize(segs, per_speaker=True)
    assert all(s.speaker_label for s in segs)


def test_talk_time_sums_correctly():
    segs = transcription.transcribe(_bundle(True))
    segs = diarization.diarize(segs, per_speaker=True)
    totals = diarization.compute_talk_time(segs)
    assert sum(totals.values()) > 0


def test_classification_returns_tone_and_themes():
    segs = transcription.transcribe(_bundle(True))
    result = classification.classify(segs)
    assert result["overall_tone"] in {"positif", "neutre", "négatif"}
    assert len(result["themes"]) >= 1


def test_summary_extracts_decisions_and_actions():
    segs = transcription.transcribe(_bundle(True))
    cr = summary.summarize(segs, "Point hebdo")
    assert "summary_md" in cr
    assert isinstance(cr["actions"], list)
    assert len(cr["actions"]) >= 1  # le script mock contient des actions


def test_cost_estimation_is_zero_in_mock():
    assert transcription.estimated_cost_eur(3600) == 0.0


def test_due_date_parsing():
    assert summary.parse_due_date("2026-07-01") is not None
    assert summary.parse_due_date(None) is None
    assert summary.parse_due_date("bientôt") is None
