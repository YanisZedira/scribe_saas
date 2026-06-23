"""Fabrique de sources audio : résout la bonne implémentation selon le mode."""

from __future__ import annotations

from app.audio_source.base import AudioSource
from app.audio_source.bot_source import BotSource
from app.audio_source.dictaphone import DictaphoneSource
from app.audio_source.livekit_source import LiveKitSource
from app.audio_source.vexa_source import VexaSource
from app.config import settings
from app.models import CaptureMode


def get_audio_source(mode: CaptureMode, platform: str | None = None) -> AudioSource:
    """Retourne la source adaptée au mode de captation et à la plateforme.

    - ``DICTAPHONE`` → ``DictaphoneSource``
    - ``VISIO`` + plateforme externe (meet/teams/zoom) → ``VexaSource`` (défaut)
      ou ``BotSource`` (Recall.ai) si ``VISIO_PROVIDER=recall``
    - ``VISIO`` + plateforme propre → ``LiveKitSource``
    """
    if mode == CaptureMode.DICTAPHONE:
        return DictaphoneSource()

    external = {"teams", "meet", "google_meet", "zoom", "webex"}
    if platform and platform.lower() in external:
        return BotSource() if settings.visio_provider == "recall" else VexaSource()
    if settings.visio_provider == "vexa":
        return VexaSource()
    if settings.visio_provider == "recall":
        return BotSource()
    return LiveKitSource()
