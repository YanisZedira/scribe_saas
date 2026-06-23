"""Route tableau de bord : indicateurs agrégés sur les réunions de l'utilisateur."""

from __future__ import annotations

from collections import Counter

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.auth import get_current_user
from app.database import get_session
from app.models import Action, ActionStatus, Meeting, Theme, User
from app.schemas import DashboardStats

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardStats)
def stats(user: User = Depends(get_current_user),
          session: Session = Depends(get_session)):
    meetings = session.exec(
        select(Meeting).where(Meeting.owner_id == user.id)).all()
    ids = [m.id for m in meetings]

    total_minutes = round(sum((m.duration_sec or 0) for m in meetings) / 60, 1)
    total_cost = round(sum(m.cost_eur for m in meetings), 4)

    open_actions = late_actions = 0
    themes_counter: Counter[str] = Counter()
    if ids:
        actions = session.exec(select(Action).where(Action.meeting_id.in_(ids))).all()
        open_actions = sum(a.status == ActionStatus.OPEN for a in actions)
        late_actions = sum(a.status == ActionStatus.LATE for a in actions)
        for t in session.exec(select(Theme).where(Theme.meeting_id.in_(ids))).all():
            themes_counter[t.label] += t.weight

    top = [{"label": k, "score": round(v, 2)}
           for k, v in themes_counter.most_common(5)]

    return DashboardStats(
        total_meetings=len(meetings), total_minutes=total_minutes,
        open_actions=open_actions, late_actions=late_actions,
        top_themes=top, total_cost_eur=total_cost,
    )
