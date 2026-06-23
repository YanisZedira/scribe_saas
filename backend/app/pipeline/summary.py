"""Génération du compte-rendu structuré + extraction des actions (sortie JSON).

Palier cible : CR structuré (décisions, actions avec responsable et échéance) en
JSON, rendu proprement en Markdown. Fallback déterministe sans LLM.
"""

from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone

from app.pipeline.llm import complete_json
from app.pipeline.transcription import TranscriptSegment


def summarize(segments: list[TranscriptSegment], title: str) -> dict:
    """Produit ``{summary_md, decisions, actions}`` à partir des segments."""
    transcript = "\n".join(
        f"[{s.speaker_label or '?'}] {s.text}" for s in segments
    )

    fallback = _heuristic_summary(segments, title)

    result = complete_json(
        system=(
            "Tu es un assistant qui rédige des comptes-rendus de réunion. "
            "Renvoie un JSON avec les clés : 'summary' (résumé en 3-5 phrases), "
            "'decisions' (liste de chaînes), et 'actions' (liste d'objets "
            "{description, assignee, due_date au format YYYY-MM-DD ou null})."
        ),
        user=f"Titre : {title}\n\nTranscription :\n{transcript[:8000]}",
        fallback=fallback,
    )
    result["summary_md"] = _render_markdown(title, result)
    return result


def _heuristic_summary(segments: list[TranscriptSegment], title: str) -> dict:
    """Extraction par mots-clés (décisions / actions) — testable, sans coût."""
    decisions, actions = [], []
    for seg in segments:
        low = seg.text.lower()
        if "décision" in low or "on repousse" in low or "on valide" in low:
            decisions.append(seg.text)
        if low.startswith("action") or "je m'en occupe" in low or "je vise" in low \
                or "je peux prendre" in low:
            actions.append({
                "description": seg.text,
                "assignee": seg.speaker_label,
                "due_date": _guess_due_date(seg.text),
            })
    summary = (
        f"Réunion « {title} » : {len(segments)} interventions. "
        f"{len(decisions)} décision(s) et {len(actions)} action(s) identifiées."
    )
    return {"summary": summary, "decisions": decisions, "actions": actions}


def _guess_due_date(text: str) -> str | None:
    low = text.lower()
    today = datetime.now(timezone.utc).date()
    weekdays = {"lundi": 0, "mardi": 1, "mercredi": 2, "jeudi": 3,
                "vendredi": 4, "samedi": 5, "dimanche": 6}
    for name, idx in weekdays.items():
        if name in low:
            delta = (idx - today.weekday()) % 7 or 7
            return (today + timedelta(days=delta)).isoformat()
    if "ce soir" in low or "aujourd'hui" in low:
        return today.isoformat()
    return None


def _render_markdown(title: str, data: dict) -> str:
    lines = [f"# Compte-rendu — {title}", "", "## Résumé", data.get("summary", "")]
    decisions = data.get("decisions", [])
    if decisions:
        lines += ["", "## Décisions"] + [f"- {d}" for d in decisions]
    actions = data.get("actions", [])
    if actions:
        lines += ["", "## Actions"]
        for a in actions:
            who = a.get("assignee") or "—"
            when = a.get("due_date") or "non datée"
            lines.append(f"- **{who}** — {a.get('description')} _(échéance : {when})_")
    return "\n".join(lines)


def parse_due_date(value: str | None) -> datetime | None:
    if not value:
        return None
    if not re.match(r"^\d{4}-\d{2}-\d{2}", value):
        return None
    try:
        return datetime.fromisoformat(value).replace(tzinfo=timezone.utc)
    except ValueError:
        return None
