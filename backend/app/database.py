"""Initialisation de la base de données et session SQLModel."""

from __future__ import annotations

from collections.abc import Generator

from sqlmodel import Session, SQLModel, create_engine

from app.config import settings

# ``check_same_thread`` requis uniquement pour SQLite en contexte multi-thread.
_connect_args = (
    {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
)

engine = create_engine(settings.database_url, echo=False, connect_args=_connect_args)


def init_db() -> None:
    """Crée les tables si elles n'existent pas (dev / démo).

    En production, on privilégie des migrations Alembic.
    """
    # Import nécessaire pour enregistrer les modèles dans les métadonnées.
    from app import models  # noqa: F401

    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """Dépendance FastAPI : fournit une session transactionnelle."""
    with Session(engine) as session:
        yield session
