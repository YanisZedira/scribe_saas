"""Agents IA spécialisés de Scribe.

Chaque agent a **une seule responsabilité**, un **prompt système JSON strict**, et
un **fallback déterministe** (sans LLM, budget 0 €). Ils sont orchestrés en chaîne
pour produire un compte-rendu de qualité maximale.
"""

from app.agents.specialists import (ActionAgent, ClassifierAgent, InsightsAgent,
                                    SpeakerAgent, SummarizerAgent)

#: Registre des agents (utile pour exposer les specs côté API/UI).
AGENTS = {
    "speaker": SpeakerAgent,
    "classifier": ClassifierAgent,
    "summarizer": SummarizerAgent,
    "action": ActionAgent,
    "insights": InsightsAgent,
}

__all__ = ["AGENTS", "ActionAgent", "ClassifierAgent", "InsightsAgent",
           "SpeakerAgent", "SummarizerAgent"]
