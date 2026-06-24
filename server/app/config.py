"""Configuration (variables d'environnement, .env)."""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    secret_key: str = "change-moi"
    database_url: str = "sqlite:///./scribe.db"
    cors_origins: str = "http://localhost:5173"
    token_minutes: int = 60 * 24 * 7

    # Vexa (bot Teams + transcription)
    vexa_api_url: str = "https://api.cloud.vexa.ai"
    vexa_api_key: str | None = None
    vexa_poll_interval_sec: int = 5
    vexa_poll_timeout_sec: int = 2 * 3600

    # LLM (analyse) — API compatible OpenAI
    llm_base_url: str = "https://api.mistral.ai/v1"
    llm_api_key: str | None = None
    llm_model: str = "mistral-small-latest"

    @property
    def cors_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
