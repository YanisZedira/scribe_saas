"""Vexa : envoie un bot dans une réunion Teams/Meet/Zoom et récupère le transcript.

Vexa transcrit lui-même (STT inclus) → on récupère directement le texte par
locuteur. Sans clé VEXA_API_KEY, un transcript d'exemple est renvoyé (démo).
Réf : https://docs.vexa.ai/api/bots — https://docs.vexa.ai/api/transcripts
"""

from __future__ import annotations

import re
import time
from urllib.parse import parse_qs, urlparse

import httpx

from app.config import settings


class VexaError(RuntimeError):
    pass


def parse_url(url: str) -> tuple[str, str, str | None]:
    """(platform, native_id, passcode) depuis un lien Teams/Meet/Zoom."""
    u = urlparse(url.strip())
    host = (u.hostname or "").lower()
    qs = parse_qs(u.query)
    if "teams." in host:
        m = re.search(r"/meet/(\d+)", u.path) or re.search(r"(\d{10,})", u.path)
        if not m:
            raise VexaError("Lien Teams non reconnu (ex: teams.live.com/meet/<ID>?p=<CODE>).")
        return "teams", m.group(1), (qs.get("p") or qs.get("passcode") or [None])[0]
    if "meet.google.com" in host:
        code = u.path.strip("/").split("/")[-1]
        if not re.match(r"^[a-z]{3}-[a-z]{4}-[a-z]{3}$", code):
            raise VexaError("Lien Google Meet invalide.")
        return "google_meet", code, None
    if "zoom.us" in host:
        m = re.search(r"/j/(\d+)", u.path) or re.search(r"(\d{9,})", u.path)
        if not m:
            raise VexaError("Lien Zoom non reconnu.")
        return "zoom", m.group(1), (qs.get("pwd") or [None])[0]
    raise VexaError("Plateforme non reconnue (Teams, Google Meet ou Zoom).")


def _headers() -> dict:
    return {"X-API-Key": settings.vexa_api_key or "", "Content-Type": "application/json"}


def send_bot(url: str, language: str = "fr") -> tuple[str, str]:
    platform, native_id, passcode = parse_url(url)
    if not settings.vexa_api_key:
        return platform, native_id
    payload = {"platform": platform, "native_meeting_id": native_id,
               "language": language, "bot_name": "Scribe",
               "recording_enabled": True, "transcribe_enabled": True,
               "transcription_tier": "realtime"}
    if passcode:
        payload["passcode"] = passcode
    r = httpx.post(f"{settings.vexa_api_url}/bots", headers=_headers(),
                   json=payload, timeout=30)
    if r.status_code >= 400:
        raise VexaError(f"Vexa /bots a échoué ({r.status_code}): {r.text[:200]}")
    return platform, native_id


def fetch_transcript(platform: str, native_id: str, *, wait: bool = True) -> str:
    """Texte de la réunion (lignes 'Locuteur: texte')."""
    if not settings.vexa_api_key:
        return _DEMO_TRANSCRIPT
    url = f"{settings.vexa_api_url}/transcripts/{platform}/{native_id}"
    deadline = time.time() + settings.vexa_poll_timeout_sec
    segments = []
    while True:
        r = httpx.get(url, headers=_headers(), timeout=30)
        if r.status_code == 200:
            data = r.json()
            segments = data.get("segments", []) or segments
            if not wait or data.get("status") in {"completed", "failed", "stopped"}:
                break
        if not wait or time.time() > deadline:
            break
        time.sleep(settings.vexa_poll_interval_sec)
    try:
        httpx.delete(f"{settings.vexa_api_url}/bots/{platform}/{native_id}",
                     headers=_headers(), timeout=15)
    except httpx.HTTPError:
        pass
    lines = [f"{s.get('speaker') or 'Intervenant'}: {(s.get('text') or '').strip()}"
             for s in segments if (s.get("text") or "").strip()]
    return "\n".join(lines)


_DEMO_TRANSCRIPT = """Camille: Bonjour à tous, on démarre le point produit hebdomadaire.
Aymen: Premier sujet, le retard sur l'intégration du module de paiement.
Camille: Oui, deux jours de retard à cause d'un bug d'intégration.
Aymen: Je prends le correctif, je vise une livraison pour vendredi.
Camille: Décision : on repousse la mise en production à lundi prochain.
Aymen: Il faut prévenir le client du décalage.
Camille: Action : j'envoie un e-mail au client avant ce soir.
Aymen: Dernier point, surveiller le budget API sur les longues réunions.
Camille: Bonne remarque, on met un garde-fou. Merci à tous."""
