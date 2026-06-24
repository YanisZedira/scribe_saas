"""LiveKit Agent — intercepte l'audio d'une room et le transcrit (mode visio).

Architecture d'intégration :
    Navigateur (Next.js) ──WebRTC──> Serveur LiveKit (auto-hébergé)
                                          │  (le bot rejoint la room)
                                          ▼
                                  livekit_agent.py  ── ce worker
                                          │  (1 AudioStream par participant)
                                          ▼
                              Faster-Whisper (STT local)
                                          │
                                          ▼
                          POST /api/meetings/{id}/segment  (FastAPI)

Chaque participant a sa propre piste audio → la diarisation visio est NATIVE :
on connaît "qui parle" sans modèle de diarisation (l'identité = le locuteur).

Lancement :
    python livekit_agent.py dev      # mode dev
    python livekit_agent.py start    # mode worker (prod)

Dépendances : livekit-agents, livekit (rtc), numpy, soundfile.
Variables d'env : LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET, SCRIBE_API_URL.
"""

from __future__ import annotations

import asyncio
import os
import tempfile
import wave

import httpx
import numpy as np
from dotenv import load_dotenv
from livekit import rtc
from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli

# Charge LIVEKIT_URL / LIVEKIT_API_KEY / LIVEKIT_API_SECRET depuis backend/.env
load_dotenv()

SCRIBE_API_URL = os.getenv("SCRIBE_API_URL", "http://localhost:8000")
# Si défini, le service GPU Faster-Whisper large-v3 transcrit (qualité max).
STT_ENDPOINT_URL = os.getenv("STT_ENDPOINT_URL")
STT_ENDPOINT_KEY = os.getenv("STT_ENDPOINT_KEY")
CHUNK_SECONDS = 8.0           # fenêtre de transcription glissante
SAMPLE_RATE = 16000           # Whisper attend du 16 kHz mono


async def entrypoint(ctx: JobContext) -> None:
    """Point d'entrée du worker : appelé quand le bot rejoint une room."""
    # On déduit l'ID de réunion Scribe du nom de la room (convention : meeting id).
    meeting_id = ctx.room.name
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    @ctx.room.on("track_subscribed")
    def on_track(track: rtc.Track, pub: rtc.TrackPublication,
                 participant: rtc.RemoteParticipant):
        if track.kind == rtc.TrackKind.KIND_AUDIO:
            # Une coroutine de capture par participant (= par locuteur).
            asyncio.create_task(
                _capture_track(meeting_id, track, participant.identity))

    # Maintient l'agent vivant tant que la réunion dure.
    await ctx.wait_for_disconnect()


async def _capture_track(meeting_id: str, track: rtc.Track, speaker: str) -> None:
    """Bufferise l'audio d'un participant et transcrit par fenêtres."""
    stream = rtc.AudioStream(track, sample_rate=SAMPLE_RATE, num_channels=1)
    buffer = bytearray()
    bytes_per_window = int(SAMPLE_RATE * 2 * CHUNK_SECONDS)  # 16-bit mono

    async for event in stream:
        frame = event.frame
        buffer.extend(frame.data.tobytes())
        if len(buffer) >= bytes_per_window:
            window, buffer = bytes(buffer), bytearray()
            await _transcribe_and_post(meeting_id, window, speaker)


async def _transcribe_and_post(meeting_id: str, pcm: bytes, speaker: str) -> None:
    """Écrit un WAV temporaire, transcrit (Whisper) et pousse le segment."""
    text = await asyncio.to_thread(_pcm_to_text, pcm)
    if not text:
        return
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            await client.post(
                f"{SCRIBE_API_URL}/api/meetings/{meeting_id}/segment",
                json={"speaker": speaker, "text": text},
            )
        except httpx.HTTPError:
            pass  # tolérance : on ne casse pas la réunion pour un POST raté


def _pcm_to_text(pcm: bytes) -> str:
    """Convertit un buffer PCM 16 kHz mono → fichier WAV → transcription."""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        with wave.open(tmp.name, "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(SAMPLE_RATE)
            wav.writeframes(pcm)
        path = tmp.name
    try:
        # Ignore les fenêtres quasi-silencieuses (évite les hallucinations Whisper).
        audio = np.frombuffer(pcm, dtype=np.int16).astype(np.float32) / 32768.0
        if float(np.sqrt(np.mean(audio ** 2))) < 0.005:
            return ""
        # Qualité max : on délègue au service GPU Faster-Whisper large-v3.
        if STT_ENDPOINT_URL:
            with open(path, "rb") as fh:
                headers = {"Authorization": f"Bearer {STT_ENDPOINT_KEY}"} if STT_ENDPOINT_KEY else {}
                r = httpx.post(
                    f"{STT_ENDPOINT_URL.rstrip('/')}/v1/audio/transcriptions",
                    headers=headers, files={"file": ("clip.wav", fh, "audio/wav")},
                    data={"model": "large-v3", "language": "fr"}, timeout=60)
            return (r.json().get("text") or "").strip() if r.status_code < 400 else ""
        # Repli local
        from app.ai.faster_whisper_stt import transcribe_clip
        return transcribe_clip(path)
    finally:
        os.unlink(path)


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
