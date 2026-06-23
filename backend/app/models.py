"""Modèle de données relationnel de Scribe.

Entités : User, Meeting, Speaker, Segment, Action, Theme, Consent.
Le schéma reflète l'ERD documenté dans ``docs/02_specs_architecture.md``.
"""

import enum
import uuid
from datetime import datetime, timezone

from sqlmodel import Field, Relationship, SQLModel


def _uuid() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc)


# --------------------------------------------------------------------------- #
# Énumérations métier
# --------------------------------------------------------------------------- #
class CaptureMode(str, enum.Enum):
    """Mode de captation de la réunion."""

    DICTAPHONE = "dictaphone"  # présentiel, micro de l'appareil
    VISIO = "visio"  # distance, plateforme propre ou bot


class MeetingStatus(str, enum.Enum):
    """Cycle de vie d'une réunion dans le pipeline."""

    CREATED = "created"
    RECORDING = "recording"
    UPLOADED = "uploaded"
    TRANSCRIBING = "transcribing"
    ANALYZING = "analyzing"
    DONE = "done"
    FAILED = "failed"


class ActionStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    LATE = "late"


# --------------------------------------------------------------------------- #
# Entités
# --------------------------------------------------------------------------- #
class User(SQLModel, table=True):
    """Utilisateur authentifié, propriétaire de ses réunions."""

    __tablename__ = "user"

    id: str = Field(default_factory=_uuid, primary_key=True)
    email: str = Field(index=True, unique=True)
    full_name: str | None = None
    hashed_password: str
    created_at: datetime = Field(default_factory=_now)
    retention_days: int = Field(default=90)  # RGPD : rétention configurable

    meetings: list["Meeting"] = Relationship(back_populates="owner")


class Meeting(SQLModel, table=True):
    """Une réunion captée et traitée."""

    __tablename__ = "meeting"

    id: str = Field(default_factory=_uuid, primary_key=True)
    owner_id: str = Field(foreign_key="user.id", index=True)
    title: str
    mode: CaptureMode
    status: MeetingStatus = Field(default=MeetingStatus.CREATED)
    platform: str | None = None  # "livekit" | "teams" | "meet" | "zoom" | None
    language: str = Field(default="fr")

    started_at: datetime = Field(default_factory=_now)
    duration_sec: int | None = None

    platform_ref: str | None = None  # URL/ID de réunion visio (Vexa)

    # Sorties d'analyse
    overall_tone: str | None = None  # ton global (cible : par segment dans Segment)
    summary_md: str | None = None  # compte-rendu rendu en Markdown
    decisions_json: str | None = None  # décisions structurées (JSON)
    insights_json: str | None = None  # risques / suivis / prochaines étapes (JSON)
    error_message: str | None = None

    # Coût réel observé (€) — pour le suivi budget API
    cost_eur: float = Field(default=0.0)

    # RGPD
    consent_obtained: bool = Field(default=False)
    expires_at: datetime | None = None  # date d'effacement automatique

    owner: User = Relationship(back_populates="meetings")
    speakers: list["Speaker"] = Relationship(
        back_populates="meeting",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    segments: list["Segment"] = Relationship(
        back_populates="meeting",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    actions: list["Action"] = Relationship(
        back_populates="meeting",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    themes: list["Theme"] = Relationship(
        back_populates="meeting",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class Speaker(SQLModel, table=True):
    """Locuteur identifié par la diarisation (ex. "Locuteur 1" → "Alice")."""

    __tablename__ = "speaker"

    id: str = Field(default_factory=_uuid, primary_key=True)
    meeting_id: str = Field(foreign_key="meeting.id", index=True)
    label: str  # libellé technique issu de la diarisation ("SPEAKER_00")
    display_name: str | None = None  # nom humain (avancé : identification nominative)
    talk_time_sec: float = Field(default=0.0)  # temps de parole cumulé

    meeting: Meeting = Relationship(back_populates="speakers")
    segments: list["Segment"] = Relationship(back_populates="speaker")


class Segment(SQLModel, table=True):
    """Un segment de transcription attribué à un locuteur."""

    __tablename__ = "segment"

    id: str = Field(default_factory=_uuid, primary_key=True)
    meeting_id: str = Field(foreign_key="meeting.id", index=True)
    speaker_id: str | None = Field(default=None, foreign_key="speaker.id")
    start_sec: float
    end_sec: float
    text: str
    tone: str | None = None  # classification par segment (cible)
    urgency: str | None = None  # "faible" | "normale" | "élevée"

    meeting: Meeting = Relationship(back_populates="segments")
    speaker: Speaker | None = Relationship(back_populates="segments")


class Action(SQLModel, table=True):
    """Action / décision extraite du compte-rendu, avec responsable et échéance."""

    __tablename__ = "action"

    id: str = Field(default_factory=_uuid, primary_key=True)
    meeting_id: str = Field(foreign_key="meeting.id", index=True)
    description: str
    assignee: str | None = None  # responsable (peut référencer un Speaker.display_name)
    due_date: datetime | None = None
    priority: str | None = Field(default="normale")  # basse | normale | haute
    status: ActionStatus = Field(default=ActionStatus.OPEN)
    created_at: datetime = Field(default_factory=_now)

    meeting: Meeting = Relationship(back_populates="actions")


class Theme(SQLModel, table=True):
    """Thème détecté dans la réunion (pour filtres et tendances)."""

    __tablename__ = "theme"

    id: str = Field(default_factory=_uuid, primary_key=True)
    meeting_id: str = Field(foreign_key="meeting.id", index=True)
    label: str
    weight: float = Field(default=1.0)  # importance relative (0–1)

    meeting: Meeting = Relationship(back_populates="themes")


class Consent(SQLModel, table=True):
    """Trace de consentement d'un participant (RGPD — preuve)."""

    __tablename__ = "consent"

    id: str = Field(default_factory=_uuid, primary_key=True)
    meeting_id: str = Field(foreign_key="meeting.id", index=True)
    participant_label: str
    consented: bool = Field(default=False)
    timestamp: datetime = Field(default_factory=_now)
