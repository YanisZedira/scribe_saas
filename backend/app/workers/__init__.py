"""File de tâches : traitement asynchrone (palier avancé) avec fallback synchrone."""

from app.workers.queue import enqueue_processing

__all__ = ["enqueue_processing"]
