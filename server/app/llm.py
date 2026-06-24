"""Analyse LLM : transcription → JSON (résumé, décisions, actions, points, ton).

API compatible OpenAI (Mistral par défaut). Sans clé, un repli heuristique
fournit une analyse simple pour que l'app reste fonctionnelle en démo.
"""

from __future__ import annotations

import json
import re
from datetime import date

import httpx

from app.config import settings

SYSTEM = (
    "Tu es Scribe Analyst, un moteur d'analyse de réunions. À partir de la "
    "TRANSCRIPTION (lignes 'Locuteur: texte'), tu renvoies UNIQUEMENT un objet "
    "JSON valide, sans texte autour, avec EXACTEMENT ces clés :\n"
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
    "relatives (vendredi, lundi prochain, ce soir) par rapport à DATE_DU_JOUR ; "
    "réponds dans la langue de la réunion."
)


def analyze(transcript: str) -> dict:
    fallback = _fallback(transcript)
    if not settings.llm_api_key:
        return fallback
    try:
        user = f"DATE_DU_JOUR: {date.today().isoformat()}\n\nTRANSCRIPTION:\n{transcript}"
        r = httpx.post(
            f"{settings.llm_base_url}/chat/completions",
            headers={"Authorization": f"Bearer {settings.llm_api_key}",
                     "Content-Type": "application/json"},
            json={"model": settings.llm_model,
                  "messages": [{"role": "system", "content": SYSTEM},
                               {"role": "user", "content": user}],
                  "temperature": 0.2,
                  "response_format": {"type": "json_object"}},
            timeout=90)
        r.raise_for_status()
        content = r.json()["choices"][0]["message"]["content"]
        s, e = content.find("{"), content.rfind("}")
        data = json.loads(content[s:e + 1])
        # complète les clés manquantes
        for k, v in fallback.items():
            data.setdefault(k, v)
        return data
    except Exception:  # noqa: BLE001 — dégrade proprement
        return fallback


def _fallback(transcript: str) -> dict:
    """Analyse heuristique (sans LLM) — suffisante pour la démo."""
    lines = [l for l in transcript.splitlines() if l.strip()]
    decisions, actions = [], []
    for line in lines:
        low = line.lower()
        text = line.split(":", 1)[-1].strip()
        who = line.split(":", 1)[0].strip() if ":" in line else None
        if "décision" in low or "on repousse" in low or "on valide" in low:
            decisions.append(text)
        if low.split(":", 1)[-1].strip().startswith("action") or "je m'en occupe" in low \
                or "je vise" in low or "je prends" in low or "j'envoie" in low:
            actions.append({"tache": text, "responsable": who, "echeance": None})
    return {
        "titre": "Compte-rendu de réunion",
        "resume": " ".join(lines[:3])[:400] if lines else "Réunion sans contenu.",
        "ton": "neutre",
        "themes": ["Divers"],
        "points_cles": [l.split(":", 1)[-1].strip() for l in lines[:4]],
        "decisions": decisions,
        "actions": actions,
    }
