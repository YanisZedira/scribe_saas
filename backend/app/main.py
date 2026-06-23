"""Point d'entrée FastAPI de Scribe.

Monte les routeurs API, sert le front-end SPA et expose la documentation OpenAPI.
"""

from __future__ import annotations

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import init_db
from app.routers import auth, consent, dashboard, meetings, webhooks

_STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Scribe API",
    version="1.0.0",
    description="Assistant de réunion intelligent — captation, transcription, "
                "compte-rendu et suivi.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)

for r in (auth.router, meetings.router, dashboard.router, consent.router,
          webhooks.router):
    app.include_router(r)


@app.get("/api/health", tags=["system"])
def health():
    return {
        "status": "ok",
        "stt_provider": settings.stt_provider,
        "llm_provider": settings.llm_provider,
        "visio_provider": settings.visio_provider,
        "vexa_configured": bool(settings.vexa_api_key),
        "environment": settings.environment,
    }


@app.get("/api/agents", tags=["system"])
def list_agents():
    """Fiches des agents IA spécialisés (nom, spécialité, prompt système)."""
    from app.agents import AGENTS

    return {"agents": [cls().spec() for cls in AGENTS.values()]}


# --- Front-end SPA --------------------------------------------------------- #
if os.path.isdir(_STATIC_DIR):
    app.mount("/app", StaticFiles(directory=_STATIC_DIR, html=True), name="static")

    @app.get("/", include_in_schema=False)
    def root():
        return FileResponse(os.path.join(_STATIC_DIR, "index.html"))
