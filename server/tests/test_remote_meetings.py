from app.llm import Coverage, Decision, MeetingSummary, PodcastTurn, Speaker
from app.main import app
from fastapi.testclient import TestClient


def register(client: TestClient, email: str) -> str:
    response = client.post(
        "/api/auth/register",
        json={
            "email": email,
            "password": "password-123",
            "full_name": "Remote User",
            "terms_accepted": True,
            "privacy_accepted": True,
        },
    )
    return response.json()["access_token"]


def auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def report() -> MeetingSummary:
    return MeetingSummary(
        language="fr",
        executive_summary="Le lancement est confirmé.",
        detailed_minutes="L'équipe confirme le lancement.",
        speakers=[Speaker(label="Yanis", participant_name="Yanis", confidence="explicit")],
        key_points=[],
        mentions=[],
        decisions=[Decision(decision="Lancer", decided_by=["Yanis"], segment_ids=[0])],
        actions=[],
        open_questions=[],
        risks=[],
        podcast_script=[
            PodcastTurn(host="host_a", text="Le lancement a été confirmé.", segment_ids=[0]),
            PodcastTurn(host="host_b", text="La décision est explicite.", segment_ids=[0]),
            PodcastTurn(
                host="host_a", text="Aucune action distincte n'a été attribuée.", segment_ids=[0]
            ),
            PodcastTurn(
                host="host_b", text="Le compte rendu reste fidèle à l'échange.", segment_ids=[0]
            ),
        ],
        coverage=[Coverage(segment_id=0, classification="decision", used_in=["decisions"])],
    )


def test_remote_meeting_live_and_final_report(monkeypatch):
    tokens = []
    monkeypatch.setattr("app.config.settings.smtp_host", "smtp.example.com")
    monkeypatch.setattr("app.config.settings.smtp_from_email", "scribe@example.com")
    monkeypatch.setattr("app.config.settings.vexa_api_key", "vexa-test")
    monkeypatch.setattr(
        "app.consent_routes.send_consent_email",
        lambda _name, _email, _title, token: tokens.append(token),
    )
    monkeypatch.setattr(
        "app.remote_routes.vexa.send_bot",
        lambda *_: ("google_meet", "abc-defg-hij"),
    )
    transcript = {
        "status": "active",
        "segments": [
            {
                "start_time": 0,
                "end_time": 3,
                "speaker": "Yanis",
                "text": "Le lancement est confirmé.",
                "completed": True,
            }
        ],
    }
    monkeypatch.setattr("app.remote_processing.vexa.get_transcript", lambda *_: transcript)
    monkeypatch.setattr("app.remote_processing.vexa.get_chat", lambda *_: [])
    monkeypatch.setattr("app.remote_processing.vexa.send_chat", lambda *_: None)
    monkeypatch.setattr("app.remote_processing.vexa.stop_bot", lambda *_: None)
    monkeypatch.setattr("app.remote_processing.vexa.delete_meeting", lambda *_: None)
    monkeypatch.setattr("app.remote_processing.generate_summary", lambda *_: report())

    with TestClient(app) as client:
        token = register(client, "remote@example.com")
        headers = auth(token)
        consent = client.post(
            "/api/consent-sessions",
            headers=headers,
            json={
                "title": "Lancement",
                "participants": [{"name": "Yanis", "email": "yanis@example.com"}],
            },
        ).json()
        client.post(f"/api/public/consents/{tokens[0]}/accept")
        client.post(
            f"/api/consent-sessions/{consent['id']}/start",
            headers=headers,
            json={"notice_confirmed": True},
        )
        created = client.post(
            "/api/remote-meetings",
            headers=headers,
            json={
                "consent_session_id": consent["id"],
                "meeting_url": "https://meet.google.com/abc-defg-hij",
                "language": "fr",
            },
        )
        assert created.status_code == 201
        meeting_id = created.json()["id"]

        live = client.post(f"/api/remote-meetings/{meeting_id}/sync", headers=headers)
        assert live.json()["status"] == "live"
        assert live.json()["segments"][0]["speaker"] == "Yanis"

        finished = client.post(f"/api/remote-meetings/{meeting_id}/finish", headers=headers)
        assert finished.status_code == 202
        detail = client.get(f"/api/remote-meetings/{meeting_id}", headers=headers).json()
        assert detail["status"] == "completed"
        assert detail["report"]["decisions"][0]["decision"] == "Lancer"
        assert detail["provider_data_deleted"] is True
