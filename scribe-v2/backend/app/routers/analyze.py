"""Route d'analyse IA : assemble la transcription et appelle Qwen 2.5.

``POST /api/analyze_meeting`` :
- assemble la transcription en appliquant le mapping de locuteurs renommés ;
- appelle Qwen via ``analyze_transcript`` (JSON strict + relance auto-corrective) ;
- persiste résumé, ton, thèmes et actions ;
- gère proprement les erreurs Qwen (502) et de parsing (422).
"""

from __future__ import annotations

import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ValidationError
from sqlmodel import Session

from app.ai.analyzer import analyze_transcript
from app.ai.qwen_client import QwenError
from app.auth import get_current_user
from app.database import get_session
from app.models import (Action, ActionStatus, Meeting, MeetingStatus, SpeakerMap,
                        User)

router = APIRouter(prefix="/api", tags=["analysis"])

_STATUS_MAP = {"à_faire": ActionStatus.TODO, "en_cours": ActionStatus.DOING,
               "fait": ActionStatus.DONE}


def _transcript_of(m, session) -> str:
    names = {s.label: s.display_name for s in m.speaker_maps}
    return "\n".join(f"{names.get(s.speaker_label, s.speaker_label)}: {s.text}"
                     for s in sorted(m.segments, key=lambda x: x.start_sec))


@router.get("/skills")
def list_skills():
    """Fiches des compétences IA disponibles (pour l'UI / la doc)."""
    from app.ai.qwen_prompts import SKILLS
    return {"skills": [{"name": k, "specialty": v["specialty"]}
                       for k, v in SKILLS.items()]}


class AnalyzeIn(BaseModel):
    meeting_id: str


@router.post("/analyze_meeting")
def analyze_meeting(p: AnalyzeIn, user: User = Depends(get_current_user),
                    session: Session = Depends(get_session)):
    m = session.get(Meeting, p.meeting_id)
    if not m or m.owner_id != user.id:
        raise HTTPException(404, "Réunion introuvable")
    if not m.segments:
        raise HTTPException(400, "Aucune transcription à analyser.")

    # 1) Transcription consolidée avec noms réels (mapping locuteurs) --------
    transcript = _transcript_of(m, session)

    m.status = MeetingStatus.ANALYZING
    session.add(m); session.commit()

    # 2) Analyse Qwen (avec gestion d'erreurs explicite) ---------------------
    try:
        analysis = analyze_transcript(transcript)
    except QwenError as exc:
        _fail(session, m, f"LLM injoignable : {exc}")
        raise HTTPException(502, f"Service d'analyse (Qwen) indisponible : {exc}")
    except (ValidationError, ValueError, json.JSONDecodeError) as exc:
        _fail(session, m, f"Sortie LLM non conforme : {exc}")
        raise HTTPException(422, "Le modèle n'a pas renvoyé un JSON conforme "
                                 "après relance. Réessayez.") from exc

    # 3) Persistance ---------------------------------------------------------
    m.title = analysis.titre or m.title
    m.summary = analysis.resume
    m.tone = analysis.ton
    m.themes_json = json.dumps([t.model_dump() for t in analysis.themes],
                               ensure_ascii=False)
    m.analysis_json = analysis.model_dump_json()
    for a in list(m.actions):
        session.delete(a)  # ré-analyse idempotente
    for act in analysis.actions:
        session.add(Action(meeting_id=m.id, task=act.tache,
                          assignee=act.responsable, priority=act.priorite,
                          due_date=_parse_date(act.echeance),
                          status=_STATUS_MAP.get(act.statut, ActionStatus.TODO)))
    m.status = MeetingStatus.DONE
    session.add(m); session.commit()
    return {"ok": True, "analysis": analysis.model_dump()}


class SkillIn(BaseModel):
    meeting_id: str
    skill: str  # ex: "email_suivi", "resume", "actions"...


@router.post("/skill")
def run_skill_route(p: SkillIn, user: User = Depends(get_current_user),
                    session: Session = Depends(get_session)):
    """Exécute un skill ciblé sur la transcription (ex: e-mail de suivi)."""
    from app.ai.analyzer import run_skill
    from app.ai.qwen_client import QwenError

    m = session.get(Meeting, p.meeting_id)
    if not m or m.owner_id != user.id:
        raise HTTPException(404, "Réunion introuvable")
    if not m.segments:
        raise HTTPException(400, "Aucune transcription.")
    try:
        return {"ok": True, "result": run_skill(p.skill, _transcript_of(m, session))}
    except QwenError as exc:
        raise HTTPException(502, f"LLM indisponible : {exc}") from exc
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc


def _fail(session: Session, m: Meeting, msg: str) -> None:
    m.status = MeetingStatus.FAILED
    m.error_message = msg[:400]
    session.add(m); session.commit()


def _parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value).replace(tzinfo=timezone.utc)
    except ValueError:
        return None
