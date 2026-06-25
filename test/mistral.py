"""Mistral (LLM) — analyse d'une transcription → JSON structuré.

Endpoint : POST https://api.mistral.ai/v1/chat/completions
"""

from __future__ import annotations

import json
import re
from datetime import date

import httpx

URL = "https://api.mistral.ai/v1/chat/completions"

SYSTEM = (
    "Tu es Scribe Analyst, moteur d'analyse de réunions. À partir de la "
    "TRANSCRIPTION fournie, tu renvoies UNIQUEMENT un objet JSON valide, sans "
    "texte autour, avec EXACTEMENT ces clés :\n"
    '{\n'
    '  "titre": "string (<= 8 mots)",\n'
    '  "resume": "synthèse fidèle en 3 à 5 phrases",\n'
    '  "ton": "positif | neutre | négatif | tendu | constructif",\n'
    '  "themes": ["3 à 5 thèmes courts"],\n'
    '  "points_cles": ["3 à 5 points marquants"],\n'
    '  "decisions": ["décisions réellement actées"],\n'
    '  "actions": [{"tache":"impératif","responsable":"nom ou Non assigné",'
    '"echeance":"YYYY-MM-DD ou null"}]\n'
    '}\n'
    "RÈGLES : zéro invention ; si absent -> liste vide / null ; résous les dates "
    "relatives par rapport à DATE_DU_JOUR ; réponds dans la langue de la réunion."
)


def analyze(*, api_key: str, transcript: str,
            model: str = "mistral-small-latest") -> dict:
    user = f"DATE_DU_JOUR: {date.today().isoformat()}\n\nTRANSCRIPTION:\n{transcript}"
    resp = httpx.post(
        URL,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={"model": model,
              "messages": [{"role": "system", "content": SYSTEM},
                           {"role": "user", "content": user}],
              "temperature": 0.2,
              "response_format": {"type": "json_object"}},
        timeout=120)
    if resp.status_code >= 400:
        raise RuntimeError(f"Mistral {resp.status_code}: {resp.text[:300]}")
    content = resp.json()["choices"][0]["message"]["content"]
    content = re.sub(r"^```(?:json)?|```$", "", content.strip(), flags=re.MULTILINE).strip()
    s, e = content.find("{"), content.rfind("}")
    return json.loads(content[s:e + 1])
