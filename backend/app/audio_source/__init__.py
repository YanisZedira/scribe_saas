"""Abstraction « source audio » commune aux deux modes de captation.

C'est la pièce maîtresse de l'architecture : visio et dictaphone produisent un
``AudioBundle`` identique, consommé ensuite par une chaîne de traitement unique.
"""

from app.audio_source.base import AudioBundle, AudioSource, AudioTrack
from app.audio_source.factory import get_audio_source

__all__ = ["AudioBundle", "AudioSource", "AudioTrack", "get_audio_source"]
