"""Bot de réunion via Vexa — REJOINT réellement Teams / Google Meet / Zoom.

Contrairement à LiveKit (qui héberge votre propre salle), Vexa envoie un bot dans
une réunion externe à partir de son **lien**, puis renvoie la transcription par
locuteur. C'est la brique adaptée au besoin "coller un lien Teams/Meet".

- Cloud (recommandé, 0 disque) : VEXA_API_URL=https://api.cloud.vexa.ai + clé.
- Self-host : VEXA_API_URL=http://localhost:8056.
Sans clé → mode démo (transcription d'exemple) pour que l'UI reste navigable.

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


def parse_meeting_url(url: str) -> tuple[str, str, str | None]:
    """Extrait (platform, native_meeting_id, passcode) d'un lien de réunion."""
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
            raise VexaError("Lien Zoom non reconnu (ex: zoom.us/j/<ID>).")
        return "zoom", m.group(1), (qs.get("pwd") or [None])[0]

    raise VexaError("Plateforme non reconnue (Google Meet, Teams ou Zoom attendus).")


def _headers() -> dict:
    return {"X-API-Key": settings.vexa_api_key or "", "Content-Type": "application/json"}


def send_bot(meeting_url: str, language: str = "fr") -> tuple[str, str]:
    """Envoie le bot dans la réunion. Retourne (platform, native_meeting_id)."""
    platform, native_id, passcode = parse_meeting_url(meeting_url)
    if not settings.vexa_api_key:
        return platform, native_id  # mode démo

    payload = {"platform": platform, "native_meeting_id": native_id,
               "language": language, "bot_name": "Scribe",
               "recording_enabled": True, "transcribe_enabled": True,
               "transcription_tier": "realtime"}
    if passcode:
        payload["passcode"] = passcode
    r = httpx.post(f"{settings.vexa_api_url}/bots", headers=_headers(),
                   json=payload, timeout=30)
    if r.status_code >= 400:
        raise VexaError(f"Vexa POST /bots a échoué ({r.status_code}) : {r.text[:200]}")
    return platform, native_id


def fetch_transcript(platform: str, native_id: str, *, wait: bool = True
                     ) -> list[dict]:
    """Récupère les segments transcrits. Si ``wait``, attend la fin de réunion."""
    if not settings.vexa_api_key:
        return _mock_segments()

    url = f"{settings.vexa_api_url}/transcripts/{platform}/{native_id}"
    deadline = time.time() + (settings.vexa_poll_timeout_sec if wait else 0)
    segments: list[dict] = []
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

    # stoppe le bot proprement
    try:
        httpx.delete(f"{settings.vexa_api_url}/bots/{platform}/{native_id}",
                     headers=_headers(), timeout=15)
    except httpx.HTTPError:
        pass

    return [{"speaker": s.get("speaker") or "Intervenant",
             "start_sec": float(s.get("start_time") or 0.0),
             "text": (s.get("text") or "").strip()}
            for s in segments if (s.get("text") or "").strip()]


def _mock_segments() -> list[dict]:
    script = [
        ("Camille", "Bonjour à tous, on démarre le point produit hebdomadaire."),
        ("Aymen", "Premier sujet : le retard sur l'intégration paiement."),
        ("Camille", "Deux jours de retard à cause d'un bug d'intégration."),
        ("Aymen", "Je prends le correctif, livraison visée vendredi."),
        ("Camille", "Décision : on repousse la mise en production à lundi."),
        ("Camille", "Action : j'envoie un e-mail au client avant ce soir."),
    ]
    out, t = [], 0.0
    for spk, txt in script:
        out.append({"speaker": spk, "start_sec": round(t, 1), "text": txt})
        t += 6
    return out
