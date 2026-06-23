"""Client LLM unifié (OpenAI / Anthropic / Gemini) avec fallback mock.

Expose ``complete_json`` (sortie structurée) et ``complete_text``. Toute la couche
résumé/classification s'appuie dessus sans connaître le fournisseur concret.
"""

from __future__ import annotations

import json

from app.config import settings

# Coût approximatif (€ / 1M tokens) input/output — voir docs/03_benchmark.md
LLM_COST = {
    "openai": (0.14, 0.55),     # gpt-4o-mini  ($0.15/$0.60)
    "anthropic": (0.95, 4.7),   # Claude Haiku ($1/$5)
    "gemini": (0.28, 2.3),      # Gemini 2.5 Flash ($0.30/$2.50)
    "mock": (0.0, 0.0),
}


def complete_json(system: str, user: str, *, fallback: dict) -> dict:
    """Demande une réponse JSON au LLM. Retourne ``fallback`` si indisponible."""
    provider = settings.llm_provider
    try:
        if provider == "openai" and settings.openai_api_key:
            return _openai_json(system, user)
        if provider == "anthropic" and settings.anthropic_api_key:
            return _anthropic_json(system, user)
    except Exception:  # noqa: BLE001 — robustesse : on dégrade proprement
        return fallback
    return fallback


def _openai_json(system: str, user: str) -> dict:
    from openai import OpenAI

    client = OpenAI(api_key=settings.openai_api_key)
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": system},
                  {"role": "user", "content": user}],
        response_format={"type": "json_object"},
        temperature=0.2,
    )
    return json.loads(resp.choices[0].message.content)


def _anthropic_json(system: str, user: str) -> dict:
    import anthropic

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    msg = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2000,
        system=system + " Réponds uniquement avec un objet JSON valide.",
        messages=[{"role": "user", "content": user}],
    )
    text = msg.content[0].text
    start, end = text.find("{"), text.rfind("}")
    return json.loads(text[start:end + 1])
