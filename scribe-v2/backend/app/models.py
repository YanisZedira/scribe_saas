"""Schéma relationnel de Scribe v2 (SQLModel / SQLAlchemy).

Entités : User, Meeting, Segment, SpeakerMap, Action.
- Segment      : ligne de transcription (locuteur "aveugle" + texte + bornes).
- SpeakerMap   : mapping "SPEAKER_00" → "Nom Réel" (renommage manuel dans l'UI),
                 appliqué partout via une jointure logique (pas de duplication).
- Action       : tâche extraite par Qwen, avec responsable, échéance, statut.
"""

import enum
import uuid
from datetime import datetime, timezone

from sqlmodel import Field, Relationship, SQLModel


def _uuid() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc)


class CaptureMode(str, enum.Enum):
    DICTAPHONE = "dictaphone"   # présentiel (micro)
    VISIO = "visio"             # bot Vexa rejoint Teams/Meet/Zoom
    LIVEKIT = "livekit"         # salle de réunion Scribe (visio propre)


class MeetingStatus(str, enum.Enum):
    CREATED = "created"
    RECORDING = "recording"
    PROCESSING = "processing"   # diarisation + STT
    ANALYZING = "analyzing"     # Qwen
    DONE = "done"
    FAILED = "failed"


class ActionStatus(str, enum.Enum):
    TODO = "à_faire"
    DOING = "en_cours"
    DONE = "fait"


class User(SQLModel, table=True):
    __tablename__ = "user"
    id: str = Field(default_factory=_uuid, primary_key=True)
    email: str = Field(index=True, unique=True)
    full_name: str | None = None
    hashed_password: str
    retention_days: int = 90
    created_at: datetime = Field(default_factory=_now)
    meetings: list["Meeting"] = Relationship(back_populates="owner")


class Meeting(SQLModel, table=True):
    __tablename__ = "meeting"
    id: str = Field(default_factory=_uuid, primary_key=True)
    owner_id: str = Field(foreign_key="user.id", index=True)
    title: str
    mode: CaptureMode
    status: MeetingStatus = Field(default=MeetingStatus.CREATED)
    language: str = "fr"
    room_name: str | None = None          # nom de la room LiveKit (plateforme propre)
    platform: str | None = None           # google_meet | teams | zoom (bot Vexa)
    meeting_url: str | None = None         # lien de la réunion externe (bot Vexa)

    started_at: datetime = Field(default_factory=_now)
    duration_sec: int | None = None
    consent_obtained: bool = False
    expires_at: datetime | None = None

    # Sorties d'analyse Qwen (JSON sérialisé + champs dénormalisés pratiques)
    summary: str | None = None
    tone: str | None = None
    themes_json: str | None = None
    analysis_json: str | None = None
    error_message: str | None = None

    owner: User = Relationship(back_populates="meetings")
    segments: list["Segment"] = Relationship(
        back_populates="meeting",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    speaker_maps: list["SpeakerMap"] = Relationship(
        back_populates="meeting",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    actions: list["Action"] = Relationship(
        back_populates="meeting",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"})


class Segment(SQLModel, table=True):
    """Tour de parole : locuteur aveugle (SPEAKER_xx ou identité LiveKit) + texte."""
    __tablename__ = "segment"
    id: str = Field(default_factory=_uuid, primary_key=True)
    meeting_id: str = Field(foreign_key="meeting.id", index=True)
    speaker_label: str                    # "SPEAKER_00" | identité participant
    start_sec: float = 0.0
    end_sec: float = 0.0
    text: str
    meeting: Meeting = Relationship(back_populates="segments")


class SpeakerMap(SQLModel, table=True):
    """Renommage manuel d'un locuteur (appliqué partout dans l'UI/CR)."""
    __tablename__ = "speaker_map"
    id: str = Field(default_factory=_uuid, primary_key=True)
    meeting_id: str = Field(foreign_key="meeting.id", index=True)
    label: str                            # "SPEAKER_00"
    display_name: str                     # "Camille Martin"
    color: str | None = None
    meeting: Meeting = Relationship(back_populates="speaker_maps")


class Action(SQLModel, table=True):
    __tablename__ = "action"
    id: str = Field(default_factory=_uuid, primary_key=True)
    meeting_id: str = Field(foreign_key="meeting.id", index=True)
    task: str
    assignee: str | None = None
    due_date: datetime | None = None
    priority: str = "normale"
    status: ActionStatus = Field(default=ActionStatus.TODO)
    created_at: datetime = Field(default_factory=_now)
    meeting: Meeting = Relationship(back_populates="actions")
