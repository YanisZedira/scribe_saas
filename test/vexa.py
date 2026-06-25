"""Vexa — bot qui rejoint Teams/Meet/Zoom, transcription + enregistrement.

Réf : https://docs.vexa.ai/api/bots — https://docs.vexa.ai/api/transcripts
"""

from __future__ import annotations

import re
import time
from urllib.parse import parse_qs, urlparse

import httpx


def parse_url(url: str) -> tuple[str, str, str | None]:
    """(platform, native_id, passcode) depuis un lien Teams/Meet/Zoom."""
    u = urlparse(url.strip())
    host = (u.hostname or "").lower()
    qs = parse_qs(u.query)
    if "teams." in host:
        m = re.search(r"/meet/(\d+)", u.path) or re.search(r"(\d{10,})", u.path)
        if not m:
            raise ValueError("Lien Teams non reconnu (ex: teams.live.com/meet/<ID>?p=<CODE>).")
        return "teams", m.group(1), (qs.get("p") or qs.get("passcode") or [None])[0]
    if "meet.google.com" in host:
        code = u.path.strip("/").split("/")[-1]
        if not re.match(r"^[a-z]{3}-[a-z]{4}-[a-z]{3}$", code):
            raise ValueError("Lien Google Meet invalide.")
        return "google_meet", code, None
    if "zoom.us" in host:
        m = re.search(r"/j/(\d+)", u.path) or re.search(r"(\d{9,})", u.path)
        if not m:
            raise ValueError("Lien Zoom non reconnu.")
        return "zoom", m.group(1), (qs.get("pwd") or [None])[0]
    raise ValueError("Plateforme non reconnue (Teams, Google Meet ou Zoom).")


class Vexa:
    def __init__(self, api_key: str, base_url: str = "https://api.cloud.vexa.ai"):
        self.base = base_url.rstrip("/")
        self.h = {"X-API-Key": api_key, "Content-Type": "application/json"}

    def send_bot(self, url: str, language: str = "fr") -> tuple[str, str]:
        platform, native_id, passcode = parse_url(url)
        payload = {"platform": platform, "native_meeting_id": native_id,
                   "language": language, "bot_name": "Scribe",
                   "recording_enabled": True, "transcribe_enabled": True,
                   "transcription_tier": "realtime"}
        if passcode:
            payload["passcode"] = passcode
        r = httpx.post(f"{self.base}/bots", headers=self.h, json=payload, timeout=30)
        if r.status_code >= 400:
            raise RuntimeError(f"Vexa /bots {r.status_code}: {r.text[:300]}")
        return platform, native_id

    def get_transcript(self, platform: str, native_id: str) -> dict:
        r = httpx.get(f"{self.base}/transcripts/{platform}/{native_id}",
                      headers=self.h, timeout=30)
        if r.status_code >= 400:
            raise RuntimeError(f"Vexa /transcripts {r.status_code}: {r.text[:300]}")
        return r.json()

    def wait_transcript(self, platform: str, native_id: str, *,
                        timeout_sec: int = 3600, interval_sec: int = 5,
                        on_tick=None) -> dict:
        """Attend la fin de la réunion et renvoie la réponse transcript complète."""
        deadline = time.time() + timeout_sec
        data = {}
        while time.time() < deadline:
            data = self.get_transcript(platform, native_id)
            if on_tick:
                on_tick(data.get("status"), len(data.get("segments", []) or []))
            if data.get("status") in {"completed", "failed", "stopped"}:
                break
            time.sleep(interval_sec)
        return data

    def stop_bot(self, platform: str, native_id: str) -> None:
        try:
            httpx.delete(f"{self.base}/bots/{platform}/{native_id}",
                         headers=self.h, timeout=15)
        except httpx.HTTPError:
            pass

    @staticmethod
    def transcript_text(data: dict) -> str:
        lines = [f"{s.get('speaker') or 'Intervenant'}: {(s.get('text') or '').strip()}"
                 for s in data.get("segments", []) if (s.get("text") or "").strip()]
        return "\n".join(lines)
