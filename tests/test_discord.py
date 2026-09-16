from nacl.signing import SigningKey
from fastapi.testclient import TestClient

from services.agent.utils.discord import is_discord_ping, parse_discord_interaction, verify_discord_signature


def test_discord_ping_detection() -> None:
    assert is_discord_ping({"type": 1}) is True
    assert is_discord_ping({"type": 3}) is False


def test_discord_button_maps_to_shared_event_contract() -> None:
    event = parse_discord_interaction({
        "id": "interaction-1",
        "type": 3,
        "channel_id": "channel-1",
        "member": {"user": {"id": "user-1"}},
        "message": {"id": "message-1"},
        "data": {"custom_id": "approve_audit:thread-1"},
    })

    assert event.thread_id == "thread-1"
    assert event.action_id == "approve_audit"
    assert event.user_id == "user-1"
    assert event.channel_id == "channel-1"
    assert event.message_ts == "message-1"


def test_discord_signature_verification_accepts_signed_payload() -> None:
    signing_key = SigningKey.generate()
    timestamp = "1700000000"
    body = b'{"type":1}'
    signature = signing_key.sign(timestamp.encode() + body).signature.hex()

    assert verify_discord_signature(
        signing_key.verify_key.encode().hex(),
        timestamp,
        body,
        signature,
    ) is True
    assert verify_discord_signature(
        signing_key.verify_key.encode().hex(),
        timestamp,
        body + b" ",
        signature,
    ) is False


def test_discord_endpoint_acknowledges_signed_ping(monkeypatch) -> None:
    signing_key = SigningKey.generate()
    body = b'{"type":1}'
    timestamp = "1700000000"
    signature = signing_key.sign(timestamp.encode() + body).signature.hex()
    monkeypatch.setenv("DISCORD_PUBLIC_KEY", signing_key.verify_key.encode().hex())

    from services.agent.main import app

    response = TestClient(app).post(
        "/api/discord-interaction",
        content=body,
        headers={
            "Content-Type": "application/json",
            "X-Signature-Ed25519": signature,
            "X-Signature-Timestamp": timestamp,
        },
    )

    assert response.status_code == 200
    assert response.json() == {"type": 1}