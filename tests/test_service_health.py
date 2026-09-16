from fastapi.testclient import TestClient

from services.agent.main import app as agent_app
from services.scraper.app import app as scraper_app


def test_agent_health_and_readiness_are_dependency_free() -> None:
    client = TestClient(agent_app)

    assert client.get("/health").json()["status"] == "ok"
    readiness = client.get("/ready")

    assert readiness.status_code == 200
    assert readiness.json()["status"] == "ready"
    assert readiness.json()["checks"] == {"configuration": "ok"}


def test_agent_registers_existing_routers() -> None:
    client = TestClient(agent_app)

    audit_response = client.post("/api/audit")
    assert audit_response.status_code == 200
    assert client.get("/api/state/thread-1").status_code == 404
    thread_id = audit_response.json()["thread_id"]
    slack_response = client.post("/api/slack-event", json={
        "thread_id": thread_id,
        "action_id": "approve_audit",
        "user_id": "test-user",
        "channel_id": "test-channel",
        "message_ts": "123.456",
        "event_id": "event-1",
    })
    assert slack_response.status_code == 200


def test_scraper_health_and_readiness_are_dependency_free() -> None:
    client = TestClient(scraper_app)

    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/ready").json() == {
        "status": "ready",
        "checks": {"configuration": "ok"},
    }