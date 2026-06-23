"""Routes de gestion des réunions : création, captation, consultation, actions."""

from __future__ import annotations

import os
import shutil
import tempfile

from fastapi import (APIRouter, Depends, File, Form, HTTPException,
                     UploadFile, status)
from sqlmodel import Session, select

from app.auth import get_current_user
from app.config import settings
from app.database import get_session
from app.models import (Action, ActionStatus, CaptureMode, Meeting,
                        MeetingStatus, User)
from app.schemas import (ActionRead, MeetingCreate, MeetingDetail, MeetingRead,
                         SegmentRead, SpeakerRead, ThemeRead)
from app.workers import enqueue_processing

router = APIRouter(prefix="/api/meetings", tags=["meetings"])


def _owned(meeting_id: str, user: User, session: Session) -> Meeting:
    m = session.get(Meeting, meeting_id)
    if not m or m.owner_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Réunion introuvable")
    return m


@router.post("", response_model=MeetingRead, status_code=201)
def create_meeting(payload: MeetingCreate, user: User = Depends(get_current_user),
                   session: Session = Depends(get_session)):
    """Crée une réunion. Le consentement doit être recueilli avant traitement (RGPD)."""
    meeting = Meeting(owner_id=user.id, title=payload.title, mode=payload.mode,
                      platform=payload.platform, language=payload.language,
                      consent_obtained=payload.consent_obtained)
    session.add(meeting)
    session.commit()
    session.refresh(meeting)
    return meeting


@router.post("/{meeting_id}/dictaphone", response_model=MeetingRead)
async def upload_dictaphone(meeting_id: str,
                            file: UploadFile = File(...),
                            user: User = Depends(get_current_user),
                            session: Session = Depends(get_session)):
    """Mode dictaphone : reçoit le fichier audio et lance le pipeline."""
    meeting = _owned(meeting_id, user, session)
    _guard_consent(meeting)
    if meeting.mode != CaptureMode.DICTAPHONE:
        raise HTTPException(400, "Cette réunion n'est pas en mode dictaphone")

    # Garde-fou taille (budget API / mémoire).
    suffix = os.path.splitext(file.filename or "audio.wav")[1] or ".wav"
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    size = 0
    with tmp as fh:
        while chunk := await file.read(1 << 20):
            size += len(chunk)
            if size > settings.max_upload_mb * 1024 * 1024:
                fh.close()
                os.unlink(tmp.name)
                raise HTTPException(413, "Fichier trop volumineux")
            fh.write(chunk)

    meeting.status = MeetingStatus.UPLOADED
    session.add(meeting)
    session.commit()
    enqueue_processing(meeting_id, {"audio_path": tmp.name}, session=session)
    session.refresh(meeting)
    return meeting


@router.post("/{meeting_id}/visio", response_model=MeetingRead)
def start_visio(meeting_id: str,
                meeting_url: str = Form(...),
                user: User = Depends(get_current_user),
                session: Session = Depends(get_session)):
    """Mode visio : envoie le bot Vexa dans la réunion Meet/Teams/Zoom.

    Le bot rejoint immédiatement. La transcription se récupère ensuite via
    ``POST /{id}/finalize`` (quand la réunion est terminée), ce qui évite de
    bloquer la requête pendant toute la durée de la réunion.
    """
    from app.audio_source.vexa_source import VexaError, VexaSource

    meeting = _owned(meeting_id, user, session)
    _guard_consent(meeting)
    if meeting.mode != CaptureMode.VISIO:
        raise HTTPException(400, "Cette réunion n'est pas en mode visio")

    try:
        platform, native_id, _ = VexaSource.parse_meeting_url(meeting_url)
        VexaSource().join(meeting_url=meeting_url, language=meeting.language)
    except VexaError as exc:
        raise HTTPException(400, str(exc)) from exc

    meeting.platform = platform
    meeting.platform_ref = meeting_url
    meeting.status = MeetingStatus.RECORDING
    session.add(meeting)
    session.commit()
    session.refresh(meeting)
    return meeting


@router.post("/{meeting_id}/finalize", response_model=MeetingRead)
def finalize_visio(meeting_id: str, user: User = Depends(get_current_user),
                   session: Session = Depends(get_session)):
    """Récupère la transcription Vexa et lance l'analyse (fin de réunion)."""
    meeting = _owned(meeting_id, user, session)
    if meeting.mode != CaptureMode.VISIO or not meeting.platform_ref:
        raise HTTPException(400, "Aucune réunion visio en cours pour cette entrée")
    enqueue_processing(meeting_id, {"meeting_url": meeting.platform_ref},
                       session=session)
    session.refresh(meeting)
    return meeting


@router.get("", response_model=list[MeetingRead])
def list_meetings(user: User = Depends(get_current_user),
                  session: Session = Depends(get_session)):
    stmt = select(Meeting).where(Meeting.owner_id == user.id).order_by(
        Meeting.started_at.desc())
    return session.exec(stmt).all()


@router.get("/{meeting_id}", response_model=MeetingDetail)
def get_meeting(meeting_id: str, user: User = Depends(get_current_user),
                session: Session = Depends(get_session)):
    import json

    m = _owned(meeting_id, user, session)
    try:
        decisions = json.loads(m.decisions_json) if m.decisions_json else []
    except json.JSONDecodeError:
        decisions = []
    try:
        insights = json.loads(m.insights_json) if m.insights_json else {}
    except json.JSONDecodeError:
        insights = {}
    return MeetingDetail(
        **MeetingRead.model_validate(m, from_attributes=True).model_dump(),
        speakers=[SpeakerRead.model_validate(s, from_attributes=True) for s in m.speakers],
        segments=[SegmentRead.model_validate(s, from_attributes=True)
                  for s in sorted(m.segments, key=lambda x: x.start_sec)],
        actions=[ActionRead.model_validate(a, from_attributes=True) for a in m.actions],
        themes=[ThemeRead.model_validate(t, from_attributes=True) for t in m.themes],
        decisions=decisions, insights=insights,
    )


@router.patch("/actions/{action_id}", response_model=ActionRead)
def update_action(action_id: str, status_value: ActionStatus,
                  user: User = Depends(get_current_user),
                  session: Session = Depends(get_session)):
    action = session.get(Action, action_id)
    if not action or action.meeting.owner_id != user.id:
        raise HTTPException(404, "Action introuvable")
    action.status = status_value
    session.add(action)
    session.commit()
    session.refresh(action)
    return action


@router.delete("/{meeting_id}", status_code=204)
def delete_meeting(meeting_id: str, user: User = Depends(get_current_user),
                   session: Session = Depends(get_session)):
    """Droit à l'effacement (RGPD) : suppression en cascade de la réunion."""
    m = _owned(meeting_id, user, session)
    session.delete(m)
    session.commit()


def _guard_consent(meeting: Meeting) -> None:
    if not meeting.consent_obtained:
        raise HTTPException(
            status.HTTP_428_PRECONDITION_REQUIRED,
            "Consentement des participants requis avant tout traitement (RGPD).",
        )
