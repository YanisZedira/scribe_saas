"""Contrat commun des sources audio.

Toute source (dictaphone, plateforme LiveKit, bot Teams/Meet/Zoom) doit produire
le même ``AudioBundle``. La chaîne de traitement en aval ne connaît jamais le mode
de captation : elle ne voit qu'un ``AudioBundle`` normalisé.
"""

from __future__ import annotations

import abc
from dataclasses import dataclass, field


@dataclass
class AudioTrack:
    """Une piste audio normalisée (WAV 16 kHz mono recommandé).

    Attributes:
        path: chemin local du fichier audio normalisé.
        speaker_hint: étiquette de locuteur si la source la connaît déjà
            (ex. visio multi-pistes → un participant par piste). ``None`` en
            dictaphone, où la diarisation devra inférer les locuteurs.
        duration_sec: durée de la piste.
    """

    path: str
    speaker_hint: str | None = None
    duration_sec: float = 0.0


@dataclass
class AudioBundle:
    """Résultat normalisé d'une captation, indépendant du mode.

    - En **dictaphone**, ``tracks`` contient en général une seule piste (mix micro)
      et ``per_speaker`` vaut ``False`` : la diarisation devra séparer les voix.
    - En **visio**, on peut obtenir une piste par participant
      (``per_speaker = True``) : « qui parle » est connu presque gratuitement.
    - Certaines sources (Vexa) **transcrivent elles-mêmes** : elles fournissent
      directement ``prebuilt_transcript`` (liste de dicts start_sec/end_sec/
      text/speaker_label). Le pipeline saute alors l'étape STT.
    """

    tracks: list[AudioTrack] = field(default_factory=list)
    per_speaker: bool = False
    language: str = "fr"
    total_duration_sec: float = 0.0
    prebuilt_transcript: list[dict] | None = None

    @property
    def primary_path(self) -> str | None:
        """Chemin de la première piste (mix global)."""
        return self.tracks[0].path if self.tracks else None

    @property
    def has_transcript(self) -> bool:
        return bool(self.prebuilt_transcript)


class AudioSource(abc.ABC):
    """Interface abstraite : produire un ``AudioBundle`` à partir d'une captation."""

    #: identifiant lisible de la source ("dictaphone", "livekit", "recall"…)
    name: str = "abstract"

    @abc.abstractmethod
    def acquire(self, *, meeting_id: str, **kwargs) -> AudioBundle:
        """Récupère l'audio et renvoie un bundle normalisé.

        Args:
            meeting_id: identifiant de la réunion concernée.
            **kwargs: paramètres spécifiques à la source (chemin upload, room id,
                meeting url…).

        Returns:
            Un ``AudioBundle`` prêt pour la transcription.
        """
        raise NotImplementedError

    def supports_per_speaker(self) -> bool:
        """Indique si la source fournit des pistes séparées par locuteur."""
        return False
