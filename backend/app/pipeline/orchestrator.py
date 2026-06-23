"""Orchestrateur : exécute la chaîne complète et persiste les résultats.

Unique point d'entrée, identique pour les deux modes de captation.
Séquence : acquire → (transcribe si nécessaire) → diarize → agents IA → persist.

Les agents IA spécialisés (SpeakerAgent, ClassifierAgent, SummarizerAgent,
ActionAgent, InsightsAgent) sont orchestrés en chaîne pour un résultat optimal.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from sqlmodel import Session

from app.agents import (ActionAgent, ClassifierAgent, InsightsAgent,
                        SpeakerAgent, SummarizerAgent)
from app.agents.base import TranscriptView, safe_list
from app.audio_source import get_audio_source
from app.config import settings
from app.models import (Action, ActionStatus, Meeting, MeetingStatus, Segment,
                        Speaker, Theme)
from app.pipeline import diarization, summary, transcription
from app.pipeline.transcription import TranscriptSegment


def process_meeting(meeting_id: str, session: Session, **source_kwargs) -> None:
    """Traite une réunion de bout en bout. Robuste : journalise les erreurs."""
    meeting = session.get(Meeting, meeting_id)
    if meeting is None:
        raise ValueError(f"Réunion inconnue : {meeting_id}")

    try:
        # 1. Captation (abstraction commune visio / dictaphone) --------------
        source = get_audio_source(meeting.mode, meeting.platform)
        meeting.status = MeetingStatus.TRANSCRIBING
        session.add(meeting)
        session.commit()
        bundle = source.acquire(meeting_id=meeting_id, language=meeting.language,
                                **source_kwargs)

        # 2. Transcription : fournie par la source (Vexa) ou via STT ---------
        if bundle.has_transcript:
            segments = [TranscriptSegment(
                start_sec=d["start_sec"], end_sec=d["end_sec"], text=d["text"],
                speaker_label=d.get("speaker_label")) for d in bundle.prebuilt_transcript]
        else:
            segments = transcription.transcribe(bundle)

        # 3. Diarisation -----------------------------------------------------
        segments = diarization.diarize(segments, bundle.per_speaker)
        talk_time = diarization.compute_talk_time(segments)

        meeting.status = MeetingStatus.ANALYZING
        session.add(meeting)
        session.commit()

        # 4. Agents IA (chaîne) ---------------------------------------------
        view = _build_view(meeting.title, meeting.language, segments)
        speaker_info = SpeakerAgent().run(view)
        analysis = ClassifierAgent().run(view)
        cr = SummarizerAgent().run(view)
        actions = ActionAgent().run(view)
        insights = InsightsAgent().run(view)

        _apply_segment_annotations(segments, analysis)
        names = _name_map(speaker_info)

        # 5. Persistance -----------------------------------------------------
        _persist(session, meeting, segments, talk_time, analysis, cr, actions,
                 insights, names)

        meeting.status = MeetingStatus.DONE
        meeting.duration_sec = int(bundle.total_duration_sec)
        meeting.cost_eur = transcription.estimated_cost_eur(
            0 if bundle.has_transcript else bundle.total_duration_sec)
        meeting.expires_at = datetime.now(timezone.utc) + timedelta(
            days=meeting.owner.retention_days or settings.default_retention_days)
        session.add(meeting)
        session.commit()

    except Exception as exc:  # noqa: BLE001
        meeting.status = MeetingStatus.FAILED
        meeting.error_message = str(exc)[:500]
        session.add(meeting)
        session.commit()
        raise


def _build_view(title, language, segments) -> TranscriptView:
    return TranscriptView(title=title, language=language, segments=[
        {"index": i, "speaker": s.speaker_label or "?", "start_sec": s.start_sec,
         "end_sec": s.end_sec, "text": s.text}
        for i, s in enumerate(segments)
    ])


def _apply_segment_annotations(segments, analysis) -> None:
    for ann in safe_list(analysis.get("segments")):
        idx = ann.get("index") if isinstance(ann, dict) else None
        if isinstance(idx, int) and 0 <= idx < len(segments):
            segments[idx].tone = ann.get("tone")
            segments[idx].urgency = ann.get("urgency")


def _name_map(speaker_info) -> dict[str, str]:
    out = {}
    for sp in safe_list(speaker_info.get("speakers")):
        if isinstance(sp, dict) and sp.get("label"):
            out[sp["label"]] = sp.get("display_name") or sp["label"]
    return out


def _persist(session, meeting, segments, talk_time, analysis, cr, actions,
             insights, names) -> None:
    label_to_speaker: dict[str, Speaker] = {}
    for label, secs in talk_time.items():
        display = names.get(label)
        sp = Speaker(meeting_id=meeting.id, label=label,
                     display_name=display if display and not display.startswith("SPEAKER_") else None,
                     talk_time_sec=secs)
        session.add(sp)
        session.flush()
        label_to_speaker[label] = sp

    for seg in segments:
        sp = label_to_speaker.get(seg.speaker_label or "")
        session.add(Segment(meeting_id=meeting.id, speaker_id=sp.id if sp else None,
                            start_sec=seg.start_sec, end_sec=seg.end_sec,
                            text=seg.text, tone=seg.tone, urgency=seg.urgency))

    for th in safe_list(analysis.get("themes")):
        if isinstance(th, dict) and th.get("label"):
            session.add(Theme(meeting_id=meeting.id, label=th["label"],
                              weight=float(th.get("weight", 0.5) or 0.5)))

    for act in safe_list(actions.get("actions")):
        if not isinstance(act, dict) or not act.get("description"):
            continue
        session.add(Action(meeting_id=meeting.id, description=act["description"],
                          assignee=act.get("assignee"),
                          due_date=summary.parse_due_date(act.get("due_date")),
                          priority=act.get("priority", "normale"),
                          status=ActionStatus.OPEN))

    cr["actions"] = safe_list(actions.get("actions"))
    cr["summary_md"] = summary._render_markdown(meeting.title, cr)
    meeting.summary_md = cr["summary_md"]
    meeting.overall_tone = analysis.get("overall_tone")
    meeting.decisions_json = json.dumps(safe_list(cr.get("decisions")),
                                        ensure_ascii=False)
    meeting.insights_json = json.dumps(insights, ensure_ascii=False)
    session.add(meeting)
    session.commit()
