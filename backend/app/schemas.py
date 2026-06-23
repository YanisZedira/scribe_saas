"""Schémas Pydantic (DTO) pour l'API : entrées et sorties découplées du modèle ORM."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, EmailStr

from app.models import ActionStatus, CaptureMode, MeetingStatus


# --- Auth ------------------------------------------------------------------ #
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None


class UserRead(BaseModel):
    id: str
    email: EmailStr
    full_name: str | None = None
    retention_days: int


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# --- Réunions -------------------------------------------------------------- #
class MeetingCreate(BaseModel):
    title: str
    mode: CaptureMode
    platform: str | None = None
    language: str = "fr"
    consent_obtained: bool = False


class SpeakerRead(BaseModel):
    id: str
    label: str
    display_name: str | None
    talk_time_sec: float


class SegmentRead(BaseModel):
    id: str
    speaker_id: str | None
    start_sec: float
    end_sec: float
    text: str
    tone: str | None
    urgency: str | None


class ActionRead(BaseModel):
    id: str
    description: str
    assignee: str | None
    due_date: datetime | None
    priority: str | None = "normale"
    status: ActionStatus


class ThemeRead(BaseModel):
    id: str
    label: str
    weight: float


class MeetingRead(BaseModel):
    id: str
    title: str
    mode: CaptureMode
    status: MeetingStatus
    platform: str | None
    language: str
    started_at: datetime
    duration_sec: int | None
    overall_tone: str | None
    summary_md: str | None
    cost_eur: float
    consent_obtained: bool
    expires_at: datetime | None


class MeetingDetail(MeetingRead):
    speakers: list[SpeakerRead] = []
    segments: list[SegmentRead] = []
    actions: list[ActionRead] = []
    themes: list[ThemeRead] = []
    decisions: list[str] = []
    insights: dict = {}


# --- Tableau de bord ------------------------------------------------------- #
class DashboardStats(BaseModel):
    total_meetings: int
    total_minutes: float
    open_actions: int
    late_actions: int
    top_themes: list[dict]
    total_cost_eur: float
