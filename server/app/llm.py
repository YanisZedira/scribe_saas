"""Analyse LLM (Mistral) — transcription → JSON structuré. Réel, sans fallback.

Si LLM_API_KEY est absent, lève une erreur explicite (aucune analyse factice).
"""

from __future__ import annotations

import json
import re
from datetime import date

import httpx

from app.config import settings


class LLMError(RuntimeError):
    pass


SYSTEM = (
    "Tu es Scribe Analyst, un moteur d'analyse de réunions de niveau expert. "
    "À partir de la TRANSCRIPTION (lignes « Locuteur: texte »), tu renvoies "
    "UNIQUEMENT un objet JSON valide, sans texte ni Markdown autour, avec "
    "EXACTEMENT ces clés :\n"
    "{\n"
    '  "titre": "titre court, <= 8 mots",\n'
    '  "resume": "synthèse fidèle et fluide, 4 à 6 phrases",\n'
    '  "ton": "positif | neutre | négatif | tendu | constructif",\n'
    '  "themes": ["3 à 5 thèmes courts"],\n'
    '  "points_cles": ["3 à 6 points marquants, une phrase chacun"],\n'
    '  "decisions": ["décisions réellement actées pendant la réunion"],\n'
    '  "prochaines_actions": [\n'
    '     {"action":"verbe à l\'impératif, claire et autoporteuse",\n'
    '      "responsable":"nom du locuteur si identifiable, sinon Non assigné",\n'
    '      "echeance":"YYYY-MM-DD si une date est dite, sinon null",\n'
    '      "priorite":"basse | normale | haute"}\n'
    "  ],\n"
    '  "compte_rendu_md": "compte-rendu complet rédigé en Markdown (titre, '
    'résumé, décisions, actions, points clés) prêt à être envoyé par e-mail"\n'
    "}\n\n"
    "RÈGLES STRICTES :\n"
    "- ZÉRO invention : n'ajoute aucun fait, nom, date ou décision absent.\n"
    "- Si une information manque : liste vide, ou \"Non assigné\", ou null.\n"
    "- Une décision = un engagement acté ; une action = une tâche à faire ensuite.\n"
    "- Résous les dates relatives (vendredi, lundi prochain, ce soir) par rapport "
    "à DATE_DU_JOUR.\n"
    "- Réponds dans la langue de la réunion."
)


def analyze(transcript: str) -> dict:
    if not settings.llm_api_key:
        raise LLMError("LLM_API_KEY manquant dans server/.env — requis (aucune analyse factice).")
    user = (f"DATE_DU_JOUR: {date.today().isoformat()}\n\n"
            f"TRANSCRIPTION:\n\"\"\"\n{transcript.strip()}\n\"\"\"")
    try:
        r = httpx.post(
            f"{settings.llm_base_url}/chat/completions",
            headers={"Authorization": f"Bearer {settings.llm_api_key}",
                     "Content-Type": "application/json"},
            json={"model": settings.llm_model,
                  "messages": [{"role": "system", "content": SYSTEM},
                               {"role": "user", "content": user}],
                  "temperature": 0.2,
                  "response_format": {"type": "json_object"}},
            timeout=120)
    except httpx.HTTPError as exc:
        raise LLMError(f"Mistral injoignable : {exc}") from exc
    if r.status_code >= 400:
        raise LLMError(f"Mistral {r.status_code}: {r.text[:300]}")
    content = r.json()["choices"][0]["message"]["content"]
    content = re.sub(r"^```(?:json)?|```$", "", content.strip(), flags=re.MULTILINE).strip()
    s, e = content.find("{"), content.rfind("}")
    if s == -1 or e == -1:
        raise LLMError("Réponse LLM non-JSON.")
    return json.loads(content[s:e + 1])
