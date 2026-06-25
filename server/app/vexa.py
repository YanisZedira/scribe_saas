"""Vexa : bot qui rejoint Teams/Meet/Zoom, écoute et transcrit (réel, sans mock).

Si VEXA_API_KEY est absent, les appels lèvent une erreur explicite (aucun
fallback / fausse transcription).
Réf : https://docs.vexa.ai/api/bots — https://docs.vexa.ai/api/transcripts
"""

from __future__ import annotations

import re
from urllib.parse import parse_qs, urlparse

import httpx

from app.config import settings


class VexaError(RuntimeError):
    pass


def _require_key() -> str:
    if not settings.vexa_api_key:
        raise VexaError("VEXA_API_KEY manquant dans server/.env — requis (aucun mode démo).")
    return settings.vexa_api_key


def parse_url(url: str) -> tuple[str, str, str | None]:
    """(platform, native_id, passcode) depuis un lien Teams/Meet/Zoom."""
    u = urlparse(url.strip())
    host = (u.hostname or "").lower()
    qs = parse_qs(u.query)
    if "meet.google.com" in host:
        code = u.path.strip("/").split("/")[-1]
        if not re.match(r"^[a-z]{3}-[a-z]{4}-[a-z]{3}$", code):
            raise VexaError("Lien Google Meet invalide (attendu meet.google.com/abc-defg-hij).")
        return "google_meet", code, None
    if "teams." in host:
        m = re.search(r"/meet/(\d+)", u.path) or re.search(r"(\d{10,})", u.path)
        if not m:
            raise VexaError("Lien Teams non reconnu (ex: teams.live.com/meet/<ID>?p=<CODE>).")
        return "teams", m.group(1), (qs.get("p") or qs.get("passcode") or [None])[0]
    if "zoom.us" in host:
        m = re.search(r"/j/(\d+)", u.path) or re.search(r"(\d{9,})", u.path)
        if not m:
            raise VexaError("Lien Zoom non reconnu (attendu /j/<ID>).")
        return "zoom", m.group(1), (qs.get("pwd") or [None])[0]
    raise VexaError("Plateforme non reconnue (Google Meet, Teams ou Zoom).")


def _headers() -> dict:
    return {"X-API-Key": _require_key(), "Content-Type": "application/json"}


def send_bot(url: str, language: str = "fr") -> tuple[str, str]:
    """Envoie le bot dans la réunion. Retourne (platform, native_id)."""
    platform, native_id, passcode = parse_url(url)
    payload = {"platform": platform, "native_meeting_id": native_id,
               "language": language, "bot_name": "Scribe",
               "recording_enabled": True, "transcribe_enabled": True,
               "transcription_tier": "realtime"}
    if passcode:
        payload["passcode"] = passcode
    r = httpx.post(f"{settings.vexa_api_url}/bots", headers=_headers(),
                   json=payload, timeout=30)
    if r.status_code >= 400:
        raise VexaError(f"Vexa /bots a échoué ({r.status_code}): {r.text[:300]}")
    return platform, native_id


def get_transcript(platform: str, native_id: str) -> dict:
    """Récupère l'état courant : { status, segments[...] }."""
    r = httpx.get(f"{settings.vexa_api_url}/transcripts/{platform}/{native_id}",
                  headers=_headers(), timeout=30)
    if r.status_code >= 400:
        raise VexaError(f"Vexa /transcripts a échoué ({r.status_code}): {r.text[:300]}")
    return r.json()


def stop_bot(platform: str, native_id: str) -> None:
    try:
        httpx.delete(f"{settings.vexa_api_url}/bots/{platform}/{native_id}",
                     headers=_headers(), timeout=15)
    except httpx.HTTPError:
        pass


def transcript_text(data: dict) -> str:
    lines = [f"{s.get('speaker') or 'Intervenant'}: {(s.get('text') or '').strip()}"
             for s in data.get("segments", []) if (s.get("text") or "").strip()]
    return "\n".join(lines)
