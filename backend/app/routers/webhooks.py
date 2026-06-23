"""Webhooks des plateformes visio (palier avancé).

Recall.ai notifie Scribe lorsque l'enregistrement d'un bot est prêt. On déclenche
alors le pipeline de façon asynchrone. (Signature à vérifier en production.)
"""

from __future__ import annotations

from fastapi import APIRouter, Request
from sqlmodel import Session, select

from app.database import engine
from app.models import Meeting, MeetingStatus
from app.workers import enqueue_processing

router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])


@router.post("/recall")
async def recall_webhook(request: Request):
    payload = await request.json()
    event = payload.get("event")
    bot_id = (payload.get("data") or {}).get("bot_id")
    if event in {"bot.done", "recording.done"} and bot_id:
        with Session(engine) as session:
            meeting = session.exec(
                select(Meeting).where(Meeting.platform.isnot(None))
            ).first()
            if meeting and meeting.status == MeetingStatus.RECORDING:
                enqueue_processing(meeting.id, {"bot_id": bot_id})
    return {"received": True}
