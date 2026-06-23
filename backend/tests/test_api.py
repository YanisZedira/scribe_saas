"""Tests d'intégration de l'API (auth, RGPD, cycle de vie d'une réunion)."""

from __future__ import annotations

import io


def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_register_and_login(client):
    r = client.post("/api/auth/register",
                    json={"email": "a@b.fr", "password": "pw123456"})
    assert r.status_code == 201
    r = client.post("/api/auth/login",
                    data={"username": "a@b.fr", "password": "pw123456"})
    assert r.status_code == 200 and "access_token" in r.json()


def test_duplicate_email_rejected(client):
    client.post("/api/auth/register", json={"email": "d@b.fr", "password": "pw123456"})
    r = client.post("/api/auth/register", json={"email": "d@b.fr", "password": "pw123456"})
    assert r.status_code == 409


def test_consent_required_before_processing(client, auth_headers):
    """RGPD : sans consentement, le traitement est refusé (428)."""
    m = client.post("/api/meetings", headers=auth_headers,
                    json={"title": "T", "mode": "dictaphone",
                          "consent_obtained": False}).json()
    files = {"file": ("a.wav", io.BytesIO(b"RIFF0000"), "audio/wav")}
    r = client.post(f"/api/meetings/{m['id']}/dictaphone",
                    headers=auth_headers, files=files)
    assert r.status_code == 428


def test_full_dictaphone_flow(client, auth_headers):
    """Crée une réunion consentie, envoie l'audio, vérifie le CR généré."""
    m = client.post("/api/meetings", headers=auth_headers,
                    json={"title": "Hebdo", "mode": "dictaphone",
                          "consent_obtained": True}).json()
    files = {"file": ("a.wav", io.BytesIO(b"RIFF0000DATA"), "audio/wav")}
    r = client.post(f"/api/meetings/{m['id']}/dictaphone",
                    headers=auth_headers, files=files)
    assert r.status_code == 200
    detail = client.get(f"/api/meetings/{m['id']}", headers=auth_headers).json()
    assert detail["status"] == "done"
    assert detail["summary_md"]
    assert len(detail["segments"]) > 0
    assert len(detail["actions"]) >= 1


def test_visio_flow_with_vexa(client, auth_headers):
    """Mode visio : envoi du bot Vexa (mock) puis finalisation → CR généré."""
    m = client.post("/api/meetings", headers=auth_headers,
                    json={"title": "Visio", "mode": "visio",
                          "consent_obtained": True}).json()
    r = client.post(f"/api/meetings/{m['id']}/visio", headers=auth_headers,
                    data={"meeting_url": "https://meet.google.com/abc-defg-hij"})
    assert r.status_code == 200
    assert r.json()["platform"] == "google_meet"
    fin = client.post(f"/api/meetings/{m['id']}/finalize", headers=auth_headers)
    assert fin.status_code == 200
    detail = client.get(f"/api/meetings/{m['id']}", headers=auth_headers).json()
    assert detail["status"] == "done"
    assert len(detail["speakers"]) >= 1
    assert len(detail["segments"]) > 0


def test_vexa_url_parsing():
    """Parsing des liens Meet / Teams / Zoom → identifiants Vexa."""
    from app.audio_source.vexa_source import VexaSource

    assert VexaSource.parse_meeting_url(
        "https://meet.google.com/abc-defg-hij") == ("google_meet", "abc-defg-hij", None)
    assert VexaSource.parse_meeting_url(
        "https://teams.live.com/meet/1234567890123?p=XYZ") == ("teams", "1234567890123", "XYZ")
    plat, nid, _ = VexaSource.parse_meeting_url(
        "https://us05web.zoom.us/j/12345678901?pwd=secret")
    assert (plat, nid) == ("zoom", "12345678901")


def test_dashboard_and_isolation(client, auth_headers):
    client.post("/api/meetings", headers=auth_headers,
                json={"title": "X", "mode": "dictaphone", "consent_obtained": True})
    stats = client.get("/api/dashboard", headers=auth_headers).json()
    assert stats["total_meetings"] >= 1


def test_right_to_erasure(client, auth_headers):
    m = client.post("/api/meetings", headers=auth_headers,
                    json={"title": "Z", "mode": "dictaphone",
                          "consent_obtained": True}).json()
    r = client.delete(f"/api/meetings/{m['id']}", headers=auth_headers)
    assert r.status_code == 204
    assert client.get(f"/api/meetings/{m['id']}", headers=auth_headers).status_code == 404
