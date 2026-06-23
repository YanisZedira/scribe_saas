"""Scripts prototypaux de mesure de latence des API (pytest).

Mesure p50/p95 sur des échantillons courts (budget plafonné — cf. dossier §8).
Les tests sont marqués ``latency`` et **ignorés par défaut** (nécessitent des clés
réelles). Lancement explicite :

    pytest benchmark/scripts/ -m latency -s

En l'absence de clé, un test de démonstration mesure la latence du **pipeline mock**
afin que le protocole soit exécutable sans budget.
"""

from __future__ import annotations

import os
import statistics
import time
from collections.abc import Callable

import pytest


def _measure(fn: Callable[[], None], runs: int = 5) -> dict[str, float]:
    """Exécute ``fn`` plusieurs fois et renvoie les latences agrégées (ms)."""
    samples: list[float] = []
    for _ in range(runs):
        t0 = time.perf_counter()
        fn()
        samples.append((time.perf_counter() - t0) * 1000)
    samples.sort()
    return {
        "runs": runs,
        "p50_ms": round(statistics.median(samples), 1),
        "p95_ms": round(samples[min(len(samples) - 1, int(0.95 * len(samples)))], 1),
        "mean_ms": round(statistics.mean(samples), 1),
        "min_ms": round(samples[0], 1),
        "max_ms": round(samples[-1], 1),
    }


def test_pipeline_mock_latency():
    """Mesure la latence du pipeline complet en mode mock (toujours exécutable)."""
    import sys

    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "backend"))
    from app.audio_source.base import AudioBundle, AudioTrack
    from app.pipeline import classification, diarization, summary, transcription

    def run():
        bundle = AudioBundle(tracks=[AudioTrack("<mock>/a.wav", duration_sec=60)],
                             per_speaker=True, total_duration_sec=60)
        segs = transcription.transcribe(bundle)
        segs = diarization.diarize(segs, True)
        classification.classify(segs)
        summary.summarize(segs, "Bench")

    stats = _measure(run, runs=10)
    print("\n[Pipeline mock] latence:", stats)
    assert stats["p95_ms"] < 2000  # le pipeline mock doit rester < 2 s


@pytest.mark.latency
@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OPENAI_API_KEY requis")
def test_openai_stt_latency():
    """Mesure la latence réelle de transcription OpenAI sur un échantillon court."""
    from openai import OpenAI

    client = OpenAI()
    sample = os.getenv("BENCH_AUDIO", "benchmark/samples/short.wav")
    if not os.path.exists(sample):
        pytest.skip("Échantillon audio absent (benchmark/samples/short.wav)")

    def run():
        with open(sample, "rb") as fh:
            client.audio.transcriptions.create(model="gpt-4o-transcribe", file=fh)

    stats = _measure(run, runs=3)
    print("\n[OpenAI gpt-4o-transcribe] latence:", stats)


@pytest.mark.latency
@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OPENAI_API_KEY requis")
def test_openai_llm_latency():
    """Mesure la latence d'un appel LLM de résumé (échantillon de transcription)."""
    from openai import OpenAI

    client = OpenAI()

    def run():
        client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Résume en une phrase : "
                       "réunion sur le retard de livraison, décision de reporter."}],
            max_tokens=60,
        )

    stats = _measure(run, runs=3)
    print("\n[OpenAI gpt-4o-mini] latence:", stats)
