"""Fixtures de test : base SQLite en mémoire + client FastAPI isolé."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.database import get_session
from app.main import app


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False},
                           poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session):
    app.dependency_overrides[get_session] = lambda: session
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(client):
    client.post("/api/auth/register",
                json={"email": "u@test.fr", "password": "secret123", "full_name": "U"})
    tok = client.post("/api/auth/login",
                      data={"username": "u@test.fr", "password": "secret123"})
    return {"Authorization": f"Bearer {tok.json()['access_token']}"}
