"""Abstraction de file de tâches.

- Si ``REDIS_URL`` est défini → on pousse le job dans **RQ** (worker séparé,
  palier avancé : traitement asynchrone scalable, processus distinct avec sa
  propre session BDD).
- Sinon → traitement **synchrone in-process** sur la session courante
  (palier socle/cible : suffisant pour des réunions courtes, et déterministe
  pour les tests).
"""

from __future__ import annotations

from typing import Any

from app.config import settings


def run_job(meeting_id: str, source_kwargs: dict[str, Any]) -> None:
    """Point d'entrée du job RQ (processus worker isolé → session dédiée)."""
    from sqlmodel import Session

    from app.database import engine
    from app.pipeline import process_meeting

    with Session(engine) as session:
        process_meeting(meeting_id, session, **source_kwargs)


def enqueue_processing(meeting_id: str, source_kwargs: dict[str, Any],
                       session=None) -> str:
    """Programme le traitement d'une réunion. Retourne le mode utilisé.

    Args:
        meeting_id: réunion à traiter.
        source_kwargs: paramètres passés à la source audio (audio_path, bot_id…).
        session: session BDD courante (utilisée en mode synchrone). Si ``None``
            en mode synchrone, une session dédiée est ouverte.
    """
    if settings.redis_url:
        from redis import Redis
        from rq import Queue

        q = Queue("scribe", connection=Redis.from_url(settings.redis_url))
        q.enqueue(run_job, meeting_id, source_kwargs, job_timeout=1800)
        return "async (RQ)"

    # --- Mode synchrone -----------------------------------------------------
    from app.pipeline import process_meeting

    if session is not None:
        process_meeting(meeting_id, session, **source_kwargs)
    else:
        run_job(meeting_id, source_kwargs)
    return "sync"
