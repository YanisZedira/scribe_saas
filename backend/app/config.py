"""Configuration centralisée de l'application.

Toutes les valeurs sont surchargeables par variables d'environnement (`.env`).
Chaque brique IA possède un fallback ``mock`` : l'application est entièrement
fonctionnelle de bout en bout sans aucune clé API.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Paramètres applicatifs (12-factor)."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- Général -----------------------------------------------------------
    app_name: str = "Scribe"
    environment: Literal["dev", "staging", "prod"] = "dev"
    secret_key: str = "dev-secret-change-me"
    access_token_expire_minutes: int = 60 * 24

    # --- Base de données ---------------------------------------------------
    database_url: str = "sqlite:///./scribe.db"

    # --- Fournisseurs de traitement ---------------------------------------
    stt_provider: Literal["mock", "openai", "assemblyai", "deepgram"] = "mock"
    llm_provider: Literal["mock", "openai", "anthropic", "gemini"] = "mock"
    visio_provider: Literal["mock", "vexa", "livekit", "recall"] = "vexa"

    # --- Clés API (optionnelles) ------------------------------------------
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    gemini_api_key: str | None = None
    assemblyai_api_key: str | None = None
    deepgram_api_key: str | None = None
    recall_api_key: str | None = None
    livekit_api_key: str | None = None
    livekit_api_secret: str | None = None
    livekit_url: str | None = None

    # --- Vexa (bot de réunion Meet / Teams / Zoom) ------------------------
    vexa_api_key: str | None = None
    vexa_api_url: str = "https://api.cloud.vexa.ai"  # ou http://localhost:8056
    vexa_poll_interval_sec: int = 5
    vexa_poll_timeout_sec: int = 4 * 3600

    # --- Garde-fous métier -------------------------------------------------
    max_meeting_minutes: int = 90
    max_upload_mb: int = 200
    default_retention_days: int = 90

    # --- File de tâches ----------------------------------------------------
    redis_url: str | None = None  # si None → BackgroundTasks synchrone


@lru_cache
def get_settings() -> Settings:
    """Retourne l'instance unique de configuration (mise en cache)."""
    return Settings()


settings = get_settings()
