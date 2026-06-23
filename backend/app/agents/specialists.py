"""Agents spécialisés — prompts système JSON soignés + fallbacks déterministes.

Chaîne d'orchestration recommandée :
    SpeakerAgent → ClassifierAgent → SummarizerAgent → ActionAgent → InsightsAgent
"""

from __future__ import annotations

from app.agents.base import Agent, TranscriptView, safe_list
from app.pipeline import classification as _cls
from app.pipeline import summary as _sum
from app.pipeline.transcription import TranscriptSegment


def _as_segments(view: TranscriptView) -> list[TranscriptSegment]:
    return [TranscriptSegment(start_sec=s["start_sec"], end_sec=s["end_sec"],
                              text=s["text"], speaker_label=s["speaker"])
            for s in view.segments]


# --------------------------------------------------------------------------- #
# 1. SpeakerAgent — identification / rôle des intervenants
# --------------------------------------------------------------------------- #
class SpeakerAgent(Agent):
    name = "speaker"
    specialty = "Identifie les intervenants et leur rôle probable."
    system_prompt = (
        "Tu es un expert en analyse de réunions. À partir d'une transcription "
        "annotée par locuteur (souvent des étiquettes techniques type SPEAKER_00), "
        "tu déduis pour chaque locuteur un nom affiché plausible (s'il est cité "
        "dans les propos) et un rôle probable (ex: animateur, décideur, "
        "contributeur, client).\n"
        "RÈGLES:\n"
        "- N'invente JAMAIS un nom : si aucun prénom n'est mentionné, garde "
        "l'étiquette d'origine comme display_name.\n"
        "- Réponds STRICTEMENT en JSON.\n"
        "SCHÉMA:\n"
        '{"speakers":[{"label":"SPEAKER_00","display_name":"Camille",'
        '"role":"animateur","confidence":0.0}]}'
    )

    def user_prompt(self, view: TranscriptView) -> str:
        labels = sorted({s["speaker"] for s in view.segments})
        return (f"Locuteurs: {labels}\n\nTranscription:\n{view.plain_text(6000)}")

    def fallback(self, view: TranscriptView) -> dict:
        labels = sorted({s["speaker"] for s in view.segments})
        return {"speakers": [
            {"label": l, "display_name": l if not l.startswith("SPEAKER_") else l,
             "role": "intervenant", "confidence": 0.3}
            for l in labels
        ]}


# --------------------------------------------------------------------------- #
# 2. ClassifierAgent — ton, thèmes, urgence
# --------------------------------------------------------------------------- #
class ClassifierAgent(Agent):
    name = "classifier"
    specialty = "Classe le ton global, les thèmes et le ton/urgence par segment."
    system_prompt = (
        "Tu es un analyste qui qualifie les réunions. Tu produis le ton global, "
        "3 à 6 thèmes pondérés, et pour CHAQUE segment (référencé par son index) "
        "un ton et une urgence.\n"
        "VALEURS AUTORISÉES:\n"
        "- tone ∈ {positif, neutre, négatif}\n"
        "- urgency ∈ {faible, normale, élevée}\n"
        "- weight ∈ [0,1]\n"
        "Réponds STRICTEMENT en JSON, sans texte hors JSON.\n"
        "SCHÉMA:\n"
        '{"overall_tone":"neutre","themes":[{"label":"Planning","weight":0.8}],'
        '"segments":[{"index":0,"tone":"positif","urgency":"normale"}]}'
    )

    def user_prompt(self, view: TranscriptView) -> str:
        return ("Format des lignes: index|locuteur|texte\n\n"
                + view.indexed_text(7000))

    def fallback(self, view: TranscriptView) -> dict:
        return _cls.classify(_as_segments(view))


# --------------------------------------------------------------------------- #
# 3. SummarizerAgent — compte-rendu + décisions
# --------------------------------------------------------------------------- #
class SummarizerAgent(Agent):
    name = "summarizer"
    specialty = "Rédige un compte-rendu fidèle et les décisions prises."
    system_prompt = (
        "Tu es un rédacteur de comptes-rendus de réunion professionnels, factuel "
        "et concis. Tu produis un résumé en 3 à 6 phrases et la liste des "
        "décisions explicitement prises.\n"
        "RÈGLES:\n"
        "- Reste fidèle à la transcription, n'invente rien (zéro hallucination).\n"
        "- Une décision = un engagement acté, pas une simple discussion.\n"
        "- Langue: celle de la réunion.\n"
        "- Réponds STRICTEMENT en JSON.\n"
        "SCHÉMA:\n"
        '{"summary":"...","decisions":["..."]}'
    )

    def user_prompt(self, view: TranscriptView) -> str:
        return f"Titre: {view.title}\n\nTranscription:\n{view.plain_text(8000)}"

    def fallback(self, view: TranscriptView) -> dict:
        base = _sum._heuristic_summary(_as_segments(view), view.title)
        return {"summary": base["summary"], "decisions": base["decisions"]}


# --------------------------------------------------------------------------- #
# 4. ActionAgent — extraction des actions
# --------------------------------------------------------------------------- #
class ActionAgent(Agent):
    name = "action"
    specialty = "Extrait les actions avec responsable et échéance."
    system_prompt = (
        "Tu es un chef de projet qui transforme une réunion en plan d'action "
        "opérationnel. Tu extrais chaque action concrète à réaliser.\n"
        "RÈGLES:\n"
        "- description: formulation à l'impératif, claire et autoporteuse.\n"
        "- assignee: le responsable si identifiable (nom du locuteur), sinon null.\n"
        "- due_date: au format YYYY-MM-DD si une échéance est mentionnée "
        "(résous 'vendredi', 'ce soir', 'lundi prochain'), sinon null.\n"
        "- priority ∈ {basse, normale, haute}.\n"
        "- N'invente pas d'actions: uniquement ce qui est réellement dit.\n"
        "- Réponds STRICTEMENT en JSON.\n"
        "SCHÉMA:\n"
        '{"actions":[{"description":"Envoyer un e-mail au client",'
        '"assignee":"Camille","due_date":"2026-06-22","priority":"haute"}]}'
    )

    def user_prompt(self, view: TranscriptView) -> str:
        from datetime import date
        return (f"Date du jour: {date.today().isoformat()}\n\n"
                f"Transcription:\n{view.plain_text(8000)}")

    def fallback(self, view: TranscriptView) -> dict:
        base = _sum._heuristic_summary(_as_segments(view), view.title)
        for a in base["actions"]:
            a.setdefault("priority", "normale")
        return {"actions": base["actions"]}


# --------------------------------------------------------------------------- #
# 5. InsightsAgent — risques, points de suivi, prochaines étapes
# --------------------------------------------------------------------------- #
class InsightsAgent(Agent):
    name = "insights"
    specialty = "Dégage risques, points de suivi et prochaines étapes."
    system_prompt = (
        "Tu es un consultant qui met en lumière ce qui mérite attention après une "
        "réunion. Tu identifies les risques évoqués, les points à suivre et les "
        "prochaines étapes suggérées.\n"
        "RÈGLES:\n"
        "- Reste ancré sur la transcription.\n"
        "- Sois synthétique (max 5 éléments par liste).\n"
        "- Réponds STRICTEMENT en JSON.\n"
        "SCHÉMA:\n"
        '{"risks":["..."],"follow_ups":["..."],"next_steps":["..."]}'
    )

    def user_prompt(self, view: TranscriptView) -> str:
        return view.plain_text(8000)

    def fallback(self, view: TranscriptView) -> dict:
        text = view.plain_text().lower()
        risks = []
        if "budget" in text or "tendu" in text:
            risks.append("Budget API à surveiller sur les longs audios.")
        if "retard" in text:
            risks.append("Retard de livraison susceptible d'impacter le planning.")
        return {"risks": risks, "follow_ups": [], "next_steps": []}
