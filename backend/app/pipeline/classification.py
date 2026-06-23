"""Classification du ton et des thèmes (global + par segment).

Palier socle : un ton global + une liste de thèmes.
Palier cible : ton/urgence par segment (rempli ici via heuristique + LLM optionnel).
"""

from __future__ import annotations

from app.pipeline.llm import complete_json
from app.pipeline.transcription import TranscriptSegment

# Lexiques simples pour le fallback hors-LLM (déterministe, testable).
_POSITIVE = {"parfait", "super", "merci", "d'accord", "bonne", "génial", "bravo"}
_NEGATIVE = {"retard", "bug", "problème", "tendu", "souci", "erreur", "risque"}
_URGENT = {"urgent", "aujourd'hui", "ce soir", "immédiat", "vendredi", "deadline"}


def classify(segments: list[TranscriptSegment]) -> dict:
    """Retourne ton global, thèmes pondérés et annotations par segment."""
    full_text = " ".join(s.text for s in segments)

    fallback = {
        "overall_tone": _heuristic_tone(full_text),
        "themes": _heuristic_themes(segments),
        "segments": [
            {"index": i, "tone": _heuristic_tone(s.text),
             "urgency": _heuristic_urgency(s.text)}
            for i, s in enumerate(segments)
        ],
    }

    result = complete_json(
        system=(
            "Tu es un analyste de réunions. Donne le ton global, 3 à 5 thèmes avec "
            "un poids (0-1), et pour chaque segment un ton (positif/neutre/négatif) "
            "et une urgence (faible/normale/élevée)."
        ),
        user=full_text[:6000],
        fallback=fallback,
    )

    # Applique les annotations par segment au passage.
    for ann in result.get("segments", []):
        idx = ann.get("index")
        if isinstance(idx, int) and 0 <= idx < len(segments):
            segments[idx].tone = ann.get("tone")
            segments[idx].urgency = ann.get("urgency")
    return result


def _heuristic_tone(text: str) -> str:
    t = text.lower()
    pos = sum(w in t for w in _POSITIVE)
    neg = sum(w in t for w in _NEGATIVE)
    if pos > neg:
        return "positif"
    if neg > pos:
        return "négatif"
    return "neutre"


def _heuristic_urgency(text: str) -> str:
    t = text.lower()
    return "élevée" if any(w in t for w in _URGENT) else "normale"


def _heuristic_themes(segments: list[TranscriptSegment]) -> list[dict]:
    catalogue = {
        "Livraison / planning": {"retard", "livraison", "production", "vendredi", "lundi"},
        "Technique / bug": {"bug", "module", "correctif", "intégration", "paiement"},
        "Relation client": {"client", "e-mail", "prévenir"},
        "Budget / coûts": {"budget", "api", "coût", "tendu"},
    }
    text = " ".join(s.text for s in segments).lower()
    themes = []
    for label, kw in catalogue.items():
        hits = sum(w in text for w in kw)
        if hits:
            themes.append({"label": label, "weight": round(min(hits / 3, 1.0), 2)})
    return sorted(themes, key=lambda x: -x["weight"]) or [
        {"label": "Divers", "weight": 0.5}
    ]
