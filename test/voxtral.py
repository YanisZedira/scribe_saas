"""Voxtral (Mistral) — transcription audio.

Endpoint : POST https://api.mistral.ai/v1/audio/transcriptions
Form      : file=@audio  (ou file_url=...) , model , language , timestamp_granularities
Réponse   : { text, language, segments:[{text,start,end}], usage }
Réf : https://docs.mistral.ai/capabilities/audio/
"""

from __future__ import annotations

import os

import httpx

URL = "https://api.mistral.ai/v1/audio/transcriptions"


def transcribe(*, api_key: str, model: str = "voxtral-mini-latest",
               file_path: str | None = None, file_url: str | None = None,
               language: str | None = "fr", timestamps: bool = True) -> dict:
    """Transcrit un fichier local OU une URL audio. Retourne la réponse JSON.

    Fournir soit ``file_path`` (fichier local), soit ``file_url`` (URL publique).
    """
    if not (file_path or file_url):
        raise ValueError("Fournir file_path ou file_url.")

    headers = {"x-api-key": api_key}
    data = {"model": model}
    if language:
        data["language"] = language
    if timestamps:
        data["timestamp_granularities"] = "segment"

    if file_path:
        if not os.path.exists(file_path):
            raise FileNotFoundError(file_path)
        with open(file_path, "rb") as fh:
            files = {"file": (os.path.basename(file_path), fh.read(),
                              "application/octet-stream")}
        resp = httpx.post(URL, headers=headers, data=data, files=files, timeout=300)
    else:
        data["file_url"] = file_url
        # multipart requis même pour file_url
        resp = httpx.post(URL, headers=headers, data=data,
                          files={"_": (None, "")}, timeout=300)

    if resp.status_code >= 400:
        raise RuntimeError(f"Voxtral {resp.status_code}: {resp.text[:300]}")
    return resp.json()
