"""Service d'analyse : transcription → LLM → JSON validé (robuste).

- ``analyze_transcript`` : analyse complète en une requête (chemin de prod),
  avec parsing tolérant + UNE relance auto-corrective si le JSON est invalide.
- ``run_skill`` : exécute un skill ciblé du registre (résumé, actions, e-mail…).
"""

from __future__ import annotations

import json
import re
from datetime import date

from pydantic import BaseModel, Field, ValidationError

from app.ai.qwen_client import chat_json
from app.ai.qwen_prompts import (MASTER_SYSTEM, SKILLS, build_skill_user,
                                 build_user_prompt)


# --- Validation (miroir du schéma maître) --------------------------------- #
class ActionModel(BaseModel):
    tache: str
    responsable: str = "Non assigné"
    echeance: str | None = None
    priorite: str = "normale"
    statut: str = "à_faire"


class ThemeModel(BaseModel):
    label: str
    poids: float = 0.5


class MeetingAnalysis(BaseModel):
    titre: str
    resume: str
    points_cles: list[str] = Field(default_factory=list)
    themes: list[ThemeModel] = Field(default_factory=list)
    ton: str = "neutre"
    decisions: list[str] = Field(default_factory=list)
    actions: list[ActionModel] = Field(default_factory=list)
    risques: list[str] = Field(default_factory=list)
    prochaines_etapes: list[str] = Field(default_factory=list)


def _extract_json(raw: str) -> dict:
    raw = re.sub(r"^```(?:json)?|```$", "", raw.strip(), flags=re.MULTILINE).strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        s, e = raw.find("{"), raw.rfind("}")
        if s == -1 or e == -1:
            raise
        return json.loads(raw[s:e + 1])


def analyze_transcript(transcript: str) -> MeetingAnalysis:
    """Analyse complète, validée. Lève en cas d'échec après une relance."""
    user = build_user_prompt(transcript, today=date.today().isoformat())
    raw = chat_json(MASTER_SYSTEM, user)
    try:
        return MeetingAnalysis.model_validate(_extract_json(raw))
    except (json.JSONDecodeError, ValidationError) as err:
        repair = (f"{user}\n\nTa réponse précédente était invalide "
                  f"({type(err).__name__}). Renvoie UNIQUEMENT un JSON STRICT "
                  "conforme au schéma, sans texte autour.")
        raw2 = chat_json(MASTER_SYSTEM, repair, temperature=0.0)
        return MeetingAnalysis.model_validate(_extract_json(raw2))


def run_skill(skill: str, transcript: str) -> dict:
    """Exécute un skill ciblé du registre (résumé, actions, email_suivi…)."""
    if skill not in SKILLS:
        raise ValueError(f"Skill inconnu : {skill}")
    user = build_skill_user(skill, transcript, today=date.today().isoformat())
    raw = chat_json(SKILLS[skill]["system"], user)
    return _extract_json(raw)
