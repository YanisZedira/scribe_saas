"""Routes des réunions : création, ingestion de segments (LiveKit), upload
dictaphone (pipeline PyAnnote+Whisper), renommage des locuteurs, actions.
"""

from __future__ import annotations

import os
import tempfile

from fastapi import (APIRouter, Depends, File, HTTPException, UploadFile, status)
from pydantic import BaseModel
from sqlmodel import Session, select

from app.auth import get_current_user
from app.config import settings
from app.database import get_session
from app.models import (Action, ActionStatus, CaptureMode, Meeting,
                        MeetingStatus, Segment, SpeakerMap, User)

router = APIRouter(prefix="/api/meetings", tags=["meetings"])

_PALETTE = ["#10b981", "#8b5cf6", "#38bdf8", "#f59e0b", "#fb7185", "#34d399"]


def _owned(mid: str, user: User, session: Session) -> Meeting:
    m = session.get(Meeting, mid)
    if not m or m.owner_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Réunion introuvable")
    return m


class MeetingIn(BaseModel):
    title: str
    mode: CaptureMode
    language: str = "fr"
    consent_obtained: bool = False
    meeting_url: str | None = None   # requis en visio : lien Teams/Meet/Zoom


@router.post("", status_code=201)
def create(p: MeetingIn, user: User = Depends(get_current_user),
           session: Session = Depends(get_session)):
    if not p.consent_obtained:
        raise HTTPException(428, "Consentement RGPD requis avant traitement.")
    m = Meeting(owner_id=user.id, title=p.title, mode=p.mode, language=p.language,
                consent_obtained=True)

    if p.mode == CaptureMode.VISIO:
        # Mode visio = bot Vexa qui REJOINT la réunion externe via son lien.
        from app.ai.vexa_source import VexaError, parse_meeting_url, send_bot
        if not p.meeting_url:
            raise HTTPException(400, "Lien de réunion (Teams/Meet/Zoom) requis.")
        try:
            parse_meeting_url(p.meeting_url)            # valide le lien
            platform, native_id = send_bot(p.meeting_url, p.language)
        except VexaError as exc:
            raise HTTPException(400, str(exc)) from exc
        m.platform = platform
        m.meeting_url = p.meeting_url
        m.room_name = native_id
        m.status = MeetingStatus.RECORDING

    elif p.mode == CaptureMode.LIVEKIT:
        # Salle de réunion Scribe : le LiveKit Agent (nom de room = meeting.id)
        # transcrit en temps réel via POST /segment.
        m.platform = "scribe"
        m.room_name = m.id
        m.status = MeetingStatus.RECORDING

    session.add(m); session.commit(); session.refresh(m)
    return _detail(m, session)


@router.post("/{mid}/finalize")
def finalize_visio(mid: str, user: User = Depends(get_current_user),
                   session: Session = Depends(get_session)):
    """Fin de réunion : récupère/clôture la transcription avant analyse.

    - VISIO (Vexa) : on interroge Vexa pour récupérer les segments.
    - LIVEKIT (salle Scribe) : les segments sont déjà arrivés en temps réel
      (via le LiveKit Agent → /segment), rien à récupérer.
    """
    m = _owned(mid, user, session)

    if m.mode == CaptureMode.LIVEKIT:
        last = max((s.start_sec for s in m.segments), default=0.0)
        m.duration_sec = int(last)
        m.status = MeetingStatus.PROCESSING
        session.add(m); session.commit()
        return _detail(_owned(mid, user, session), session)

    from app.ai.vexa_source import VexaError, fetch_transcript, parse_meeting_url
    if m.mode != CaptureMode.VISIO or not m.meeting_url:
        raise HTTPException(400, "Aucune réunion visio à finaliser.")
    try:
        platform, native_id, _ = parse_meeting_url(m.meeting_url)
        segments = fetch_transcript(platform, native_id, wait=True)
    except VexaError as exc:
        raise HTTPException(400, str(exc)) from exc

    m.status = MeetingStatus.PROCESSING
    last = 0.0
    for seg in segments:
        session.add(Segment(meeting_id=mid, speaker_label=seg["speaker"],
                            text=seg["text"], start_sec=seg["start_sec"]))
        _ensure_speaker(session, mid, seg["speaker"])
        last = max(last, seg["start_sec"])
    m.duration_sec = int(last)
    session.add(m); session.commit()
    return _detail(_owned(mid, user, session), session)


class SegmentIn(BaseModel):
    speaker: str
    text: str
    start_sec: float = 0.0
    end_sec: float = 0.0


@router.post("/{mid}/segment")
def add_segment(mid: str, p: SegmentIn, session: Session = Depends(get_session)):
    """Ingestion temps réel d'un segment (appelé par le LiveKit Agent)."""
    m = session.get(Meeting, mid)
    if not m:
        raise HTTPException(404, "Réunion introuvable")
    session.add(Segment(meeting_id=mid, speaker_label=p.speaker, text=p.text,
                        start_sec=p.start_sec, end_sec=p.end_sec))
    _ensure_speaker(session, mid, p.speaker)
    session.commit()
    return {"ok": True}


@router.post("/{mid}/dictaphone")
async def upload_dictaphone(mid: str, file: UploadFile = File(...),
                            user: User = Depends(get_current_user),
                            session: Session = Depends(get_session)):
    """Mode présentiel : diarisation PyAnnote + STT Whisper sur le fichier complet."""
    from app.ai.audio_pipeline import process_recording

    m = _owned(mid, user, session)
    suffix = os.path.splitext(file.filename or "a.wav")[1] or ".wav"
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    size = 0
    with tmp as fh:
        while chunk := await file.read(1 << 20):
            size += len(chunk)
            if size > settings.max_upload_mb * 1024 * 1024:
                os.unlink(tmp.name)
                raise HTTPException(413, "Fichier trop volumineux")
            fh.write(chunk)

    m.status = MeetingStatus.PROCESSING
    session.add(m); session.commit()
    try:
        result = process_recording(tmp.name, language=m.language)
    except Exception as exc:  # noqa: BLE001
        m.status = MeetingStatus.FAILED
        m.error_message = str(exc)[:400]
        session.add(m); session.commit()
        raise HTTPException(500, f"Pipeline audio échoué : {exc}") from exc
    finally:
        os.unlink(tmp.name)

    for seg in result.segments:
        session.add(Segment(meeting_id=mid, speaker_label=seg.speaker,
                            text=seg.text, start_sec=seg.start, end_sec=seg.end))
    for label in result.speakers:
        _ensure_speaker(session, mid, label)
    m.duration_sec = int(result.duration_sec)
    m.status = MeetingStatus.PROCESSING
    session.add(m); session.commit()
    return _detail(_owned(mid, user, session), session)


class RenameIn(BaseModel):
    label: str
    display_name: str


@router.patch("/{mid}/speakers")
def rename_speaker(mid: str, p: RenameIn, user: User = Depends(get_current_user),
                   session: Session = Depends(get_session)):
    """Renomme un locuteur (SPEAKER_00 → Nom Réel), appliqué partout via le mapping."""
    _owned(mid, user, session)
    sm = session.exec(select(SpeakerMap).where(
        SpeakerMap.meeting_id == mid, SpeakerMap.label == p.label)).first()
    if not sm:
        sm = SpeakerMap(meeting_id=mid, label=p.label, display_name=p.display_name)
    sm.display_name = p.display_name
    session.add(sm); session.commit()
    return {"ok": True, "label": p.label, "display_name": p.display_name}


@router.get("")
def list_meetings(user: User = Depends(get_current_user),
                  session: Session = Depends(get_session)):
    ms = session.exec(select(Meeting).where(Meeting.owner_id == user.id)
                      .order_by(Meeting.started_at.desc())).all()
    return [_summary(m) for m in ms]


@router.get("/{mid}")
def get_meeting(mid: str, user: User = Depends(get_current_user),
                session: Session = Depends(get_session)):
    return _detail(_owned(mid, user, session), session)


class ActionPatch(BaseModel):
    status: ActionStatus


@router.patch("/actions/{aid}")
def update_action(aid: str, p: ActionPatch, user: User = Depends(get_current_user),
                  session: Session = Depends(get_session)):
    a = session.get(Action, aid)
    if not a or a.meeting.owner_id != user.id:
        raise HTTPException(404, "Action introuvable")
    a.status = p.status
    session.add(a); session.commit()
    return {"ok": True}


@router.delete("/{mid}", status_code=204)
def delete_meeting(mid: str, user: User = Depends(get_current_user),
                   session: Session = Depends(get_session)):
    """Droit à l'effacement (RGPD) : suppression en cascade."""
    session.delete(_owned(mid, user, session)); session.commit()


# --- Helpers --------------------------------------------------------------- #
def _ensure_speaker(session: Session, mid: str, label: str) -> None:
    exists = session.exec(select(SpeakerMap).where(
        SpeakerMap.meeting_id == mid, SpeakerMap.label == label)).first()
    if not exists:
        n = len(session.exec(select(SpeakerMap).where(
            SpeakerMap.meeting_id == mid)).all())
        session.add(SpeakerMap(meeting_id=mid, label=label, display_name=label,
                              color=_PALETTE[n % len(_PALETTE)]))


def _summary(m: Meeting) -> dict:
    return {"id": m.id, "title": m.title, "mode": m.mode, "status": m.status,
            "started_at": m.started_at, "duration_sec": m.duration_sec,
            "tone": m.tone}


def _detail(m: Meeting, session: Session) -> dict:
    import json
    names = {s.label: s.display_name for s in m.speaker_maps}
    colors = {s.label: s.color for s in m.speaker_maps}
    try:
        analysis = json.loads(m.analysis_json) if m.analysis_json else {}
    except json.JSONDecodeError:
        analysis = {}
    return {
        **_summary(m),
        "language": m.language, "room_name": m.room_name,
        "platform": m.platform, "meeting_url": m.meeting_url,
        "consent_obtained": m.consent_obtained, "summary": m.summary,
        "analysis": analysis,
        "points_cles": analysis.get("points_cles", []),
        "decisions": analysis.get("decisions", []),
        "risques": analysis.get("risques", []),
        "prochaines_etapes": analysis.get("prochaines_etapes", []),
        "themes": json.loads(m.themes_json) if m.themes_json else [],
        "speakers": [{"label": s.label, "display_name": s.display_name,
                      "color": s.color} for s in m.speaker_maps],
        "segments": [{"id": s.id, "speaker_label": s.speaker_label,
                      "speaker": names.get(s.speaker_label, s.speaker_label),
                      "color": colors.get(s.speaker_label),
                      "start_sec": s.start_sec, "text": s.text}
                     for s in sorted(m.segments, key=lambda x: x.start_sec)],
        "actions": [{"id": a.id, "task": a.task, "assignee": a.assignee,
                     "due_date": a.due_date, "priority": a.priority,
                     "status": a.status} for a in m.actions],
    }
