"""Modèle de données : User et Meeting (transcription + analyse)."""

from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


def _uuid() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc)


class MeetingStatus(str, enum.Enum):
    JOINING = "joining"        # le bot rejoint la réunion
    RECORDING = "recording"    # en cours
    ANALYZING = "analyzing"    # transcription récupérée, analyse LLM
    DONE = "done"
    FAILED = "failed"


class User(SQLModel, table=True):
    id: str = Field(default_factory=_uuid, primary_key=True)
    email: str = Field(index=True, unique=True)
    full_name: str | None = None
    hashed_password: str
    created_at: datetime = Field(default_factory=_now)


class Meeting(SQLModel, table=True):
    id: str = Field(default_factory=_uuid, primary_key=True)
    owner_id: str = Field(foreign_key="user.id", index=True)
    title: str
    platform: str = "teams"           # teams | meet | zoom
    meeting_url: str
    native_id: str | None = None
    status: MeetingStatus = Field(default=MeetingStatus.JOINING)
    created_at: datetime = Field(default_factory=_now)
    duration_sec: int | None = None
    error: str | None = None

    # Sorties
    transcript: str | None = None     # transcription complète (texte)
    summary: str | None = None        # résumé
    decisions_json: str | None = None  # liste de décisions (JSON)
    actions_json: str | None = None    # actions {tache, responsable, echeance} (JSON)
    key_points_json: str | None = None  # points clés (JSON)
    topics_json: str | None = None     # thèmes (JSON)
    sentiment: str | None = None       # ton global
