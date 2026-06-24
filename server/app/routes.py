"""Routes API : auth, réunions (Vexa + analyse LLM), dashboard."""

from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlmodel import Session, select

from app.auth import current_user, hash_pw, make_token, verify_pw
from app.db import get_session
from app.llm import analyze
from app.models import Meeting, MeetingStatus, User
from app.vexa import VexaError, fetch_transcript, parse_url, send_bot

router = APIRouter(prefix="/api")


# ─── Auth ─────────────────────────────────────────────────────────────────
class RegisterIn(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None


@router.post("/auth/register", status_code=201)
def register(p: RegisterIn, session: Session = Depends(get_session)):
    if session.exec(select(User).where(User.email == p.email)).first():
        raise HTTPException(409, "E-mail déjà utilisé")
    u = User(email=p.email, full_name=p.full_name, hashed_password=hash_pw(p.password))
    session.add(u); session.commit()
    return {"ok": True}


@router.post("/auth/login")
def login(form: OAuth2PasswordRequestForm = Depends(),
          session: Session = Depends(get_session)):
    u = session.exec(select(User).where(User.email == form.username)).first()
    if not u or not verify_pw(form.password, u.hashed_password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Identifiants incorrects")
    return {"access_token": make_token(u.id), "token_type": "bearer"}


@router.get("/auth/me")
def me(user: User = Depends(current_user)):
    return {"id": user.id, "email": user.email, "full_name": user.full_name}


# ─── Réunions ───────────────────────────────────────────────────────────────
class MeetingIn(BaseModel):
    title: str
    meeting_url: str


def _detail(m: Meeting) -> dict:
    j = lambda s: json.loads(s) if s else []  # noqa: E731
    return {
        "id": m.id, "title": m.title, "platform": m.platform,
        "meeting_url": m.meeting_url, "status": m.status,
        "created_at": m.created_at, "duration_sec": m.duration_sec, "error": m.error,
        "transcript": m.transcript, "summary": m.summary, "sentiment": m.sentiment,
        "decisions": j(m.decisions_json), "actions": j(m.actions_json),
        "key_points": j(m.key_points_json), "topics": j(m.topics_json),
    }


def _owned(mid: str, user: User, session: Session) -> Meeting:
    m = session.get(Meeting, mid)
    if not m or m.owner_id != user.id:
        raise HTTPException(404, "Réunion introuvable")
    return m


@router.post("/meetings", status_code=201)
def create_meeting(p: MeetingIn, user: User = Depends(current_user),
                   session: Session = Depends(get_session)):
    """Envoie le bot Vexa dans la réunion Teams/Meet/Zoom."""
    try:
        platform, native_id = send_bot(p.meeting_url)
    except VexaError as exc:
        raise HTTPException(400, str(exc)) from exc
    m = Meeting(owner_id=user.id, title=p.title, meeting_url=p.meeting_url,
                platform=platform, native_id=native_id,
                status=MeetingStatus.RECORDING)
    session.add(m); session.commit(); session.refresh(m)
    return _detail(m)


@router.post("/meetings/{mid}/finalize")
def finalize(mid: str, user: User = Depends(current_user),
             session: Session = Depends(get_session)):
    """Récupère la transcription Vexa puis lance l'analyse LLM."""
    m = _owned(mid, user, session)
    try:
        platform, native_id, _ = parse_url(m.meeting_url)
        transcript = fetch_transcript(platform, native_id, wait=True)
    except VexaError as exc:
        m.status = MeetingStatus.FAILED; m.error = str(exc)
        session.add(m); session.commit()
        raise HTTPException(400, str(exc)) from exc

    if not transcript.strip():
        m.status = MeetingStatus.FAILED; m.error = "Transcription vide."
        session.add(m); session.commit()
        raise HTTPException(400, "Aucune parole transcrite.")

    m.status = MeetingStatus.ANALYZING
    m.transcript = transcript
    session.add(m); session.commit()

    a = analyze(transcript)
    m.title = a.get("titre") or m.title
    m.summary = a.get("resume")
    m.sentiment = a.get("ton")
    m.topics_json = json.dumps(a.get("themes", []), ensure_ascii=False)
    m.key_points_json = json.dumps(a.get("points_cles", []), ensure_ascii=False)
    m.decisions_json = json.dumps(a.get("decisions", []), ensure_ascii=False)
    m.actions_json = json.dumps(a.get("actions", []), ensure_ascii=False)
    m.status = MeetingStatus.DONE
    session.add(m); session.commit()
    return _detail(m)


@router.get("/meetings")
def list_meetings(user: User = Depends(current_user),
                  session: Session = Depends(get_session)):
    ms = session.exec(select(Meeting).where(Meeting.owner_id == user.id)
                      .order_by(Meeting.created_at.desc())).all()
    return [{"id": m.id, "title": m.title, "platform": m.platform,
             "status": m.status, "created_at": m.created_at,
             "sentiment": m.sentiment} for m in ms]


@router.get("/meetings/{mid}")
def get_meeting(mid: str, user: User = Depends(current_user),
                session: Session = Depends(get_session)):
    return _detail(_owned(mid, user, session))


@router.delete("/meetings/{mid}", status_code=204)
def delete_meeting(mid: str, user: User = Depends(current_user),
                   session: Session = Depends(get_session)):
    session.delete(_owned(mid, user, session)); session.commit()


# ─── Dashboard ──────────────────────────────────────────────────────────────
@router.get("/dashboard")
def dashboard(user: User = Depends(current_user),
              session: Session = Depends(get_session)):
    ms = session.exec(select(Meeting).where(Meeting.owner_id == user.id)).all()
    total_decisions = total_actions = 0
    topics: dict[str, int] = {}
    for m in ms:
        if m.decisions_json:
            total_decisions += len(json.loads(m.decisions_json))
        if m.actions_json:
            total_actions += len(json.loads(m.actions_json))
        for t in (json.loads(m.topics_json) if m.topics_json else []):
            topics[t] = topics.get(t, 0) + 1
    top = sorted(topics.items(), key=lambda x: -x[1])[:6]
    done = [m for m in ms if m.status == MeetingStatus.DONE]
    return {
        "total_meetings": len(ms),
        "analyzed": len(done),
        "total_decisions": total_decisions,
        "total_actions": total_actions,
        "top_topics": [{"label": k, "count": v} for k, v in top],
        "recent": [{"id": m.id, "title": m.title, "status": m.status,
                    "created_at": m.created_at} for m in
                   sorted(ms, key=lambda x: x.created_at, reverse=True)[:5]],
    }
