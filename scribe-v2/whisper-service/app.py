"""Micro-service de transcription SOUVERAIN — Faster-Whisper large-v3.

Conteneur autonome, à déployer sur un GPU (chez toi, ou un hébergeur EU :
Scaleway / OVHcloud). Expose une API compatible OpenAI :

    POST /v1/audio/transcriptions   (multipart: file, model?, language?)
    GET  /health

L'app Scribe pointe simplement STT_ENDPOINT_URL vers ce service. Aucune donnée
ne sort de l'infrastructure où tourne ce conteneur (argument RGPD/souveraineté).

Sécurité : si STT_API_KEY est défini, le header Authorization: Bearer <clé>
est exigé (protège un service exposé sur Internet).
"""

from __future__ import annotations

import os
import tempfile
from functools import lru_cache

from fastapi import FastAPI, File, Form, Header, HTTPException, UploadFile

MODEL = os.getenv("WHISPER_MODEL", "large-v3")
DEVICE = os.getenv("WHISPER_DEVICE", "cuda")          # "cuda" sur GPU
COMPUTE = os.getenv("WHISPER_COMPUTE_TYPE", "float16")  # "float16" GPU / "int8" CPU
API_KEY = os.getenv("STT_API_KEY")                    # protège l'endpoint (optionnel)

app = FastAPI(title="Scribe STT (Faster-Whisper)", version="1.0.0")


@lru_cache(maxsize=1)
def get_model():
    from faster_whisper import WhisperModel
    return WhisperModel(MODEL, device=DEVICE, compute_type=COMPUTE)


@app.get("/health")
def health():
    return {"status": "ok", "model": MODEL, "device": DEVICE}


@app.post("/v1/audio/transcriptions")
async def transcriptions(
    file: UploadFile = File(...),
    model: str = Form(default=MODEL),
    language: str | None = Form(default="fr"),
    authorization: str | None = Header(default=None),
):
    if API_KEY and authorization != f"Bearer {API_KEY}":
        raise HTTPException(401, "Clé API invalide")

    suffix = os.path.splitext(file.filename or "audio.webm")[1] or ".webm"
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    with tmp as fh:
        fh.write(await file.read())
    try:
        segments, info = get_model().transcribe(
            tmp.name, language=language, beam_size=5, vad_filter=True)
        text = " ".join(s.text.strip() for s in segments).strip()
    finally:
        os.unlink(tmp.name)
    return {"text": text, "language": getattr(info, "language", language)}
