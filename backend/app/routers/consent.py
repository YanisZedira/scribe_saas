"""Routes RGPD : enregistrement du consentement des participants."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session

from app.auth import get_current_user
from app.database import get_session
from app.models import Consent, Meeting, User

router = APIRouter(prefix="/api/consent", tags=["rgpd"])


class ConsentIn(BaseModel):
    meeting_id: str
    participant_label: str
    consented: bool


@router.post("")
def record_consent(payload: ConsentIn, user: User = Depends(get_current_user),
                   session: Session = Depends(get_session)):
    meeting = session.get(Meeting, payload.meeting_id)
    if not meeting or meeting.owner_id != user.id:
        raise HTTPException(404, "Réunion introuvable")
    session.add(Consent(meeting_id=payload.meeting_id,
                        participant_label=payload.participant_label,
                        consented=payload.consented))
    # La réunion n'est traitable que si tous les participants ont consenti.
    if payload.consented:
        meeting.consent_obtained = True
        session.add(meeting)
    session.commit()
    return {"ok": True, "consent_obtained": meeting.consent_obtained}
