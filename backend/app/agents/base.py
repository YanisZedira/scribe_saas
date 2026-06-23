"""Classe de base commune aux agents IA."""

from __future__ import annotations

import abc
import json
from dataclasses import dataclass

from app.pipeline.llm import complete_json


@dataclass
class TranscriptView:
    """Vue de la transcription passée aux agents (découplée de l'ORM)."""

    title: str
    language: str
    segments: list[dict]  # {index, speaker, start_sec, end_sec, text}

    def plain_text(self, limit: int = 8000) -> str:
        lines = [f"[{s['speaker']}] {s['text']}" for s in self.segments]
        return "\n".join(lines)[:limit]

    def indexed_text(self, limit: int = 8000) -> str:
        lines = [f"{s['index']}|{s['speaker']}|{s['text']}" for s in self.segments]
        return "\n".join(lines)[:limit]


class Agent(abc.ABC):
    """Agent IA : une spécialité, un prompt système JSON, un fallback robuste."""

    name: str = "agent"
    specialty: str = ""
    #: Prompt système (instructions + schéma de sortie JSON attendu).
    system_prompt: str = ""

    @abc.abstractmethod
    def user_prompt(self, view: TranscriptView) -> str:
        """Construit le message utilisateur à partir de la transcription."""

    @abc.abstractmethod
    def fallback(self, view: TranscriptView) -> dict:
        """Résultat déterministe si le LLM est indisponible (mode mock)."""

    def run(self, view: TranscriptView) -> dict:
        """Exécute l'agent. Retourne toujours un dict conforme au schéma."""
        return complete_json(
            system=self.system_prompt,
            user=self.user_prompt(view),
            fallback=self.fallback(view),
        )

    def spec(self) -> dict:
        """Expose la fiche de l'agent (pour documentation / UI)."""
        return {"name": self.name, "specialty": self.specialty,
                "system_prompt": self.system_prompt}


def safe_list(value, key: str | None = None) -> list:
    """Normalise une valeur LLM en liste (robustesse)."""
    if value is None:
        return []
    if isinstance(value, dict) and key:
        value = value.get(key, [])
    return value if isinstance(value, list) else [value]


def dumps(obj) -> str:
    return json.dumps(obj, ensure_ascii=False)
