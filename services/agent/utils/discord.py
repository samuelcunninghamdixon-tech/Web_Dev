from __future__ import annotations

import json
from typing import Any

from ..models import SlackEventRequest


def verify_discord_signature(public_key: str, timestamp: str, raw_body: bytes, signature: str) -> bool:
    if not public_key or not timestamp or not signature:
        return False
    try:
        from nacl.exceptions import BadSignatureError
        from nacl.signing import VerifyKey

        VerifyKey(bytes.fromhex(public_key)).verify(
            timestamp.encode("utf-8") + raw_body,
            bytes.fromhex(signature),
        )
    except (ValueError, BadSignatureError, ImportError):
        return False
    return True


def parse_discord_interaction(payload: dict[str, Any]) -> SlackEventRequest:
    data = payload.get("data") or {}
    custom_id = str(data.get("custom_id", ""))
    action_id, separator, thread_id = custom_id.partition(":")
    if not separator or action_id not in {"approve_audit", "request_revision", "reject_audit"}:
        raise ValueError("Discord interaction custom_id must contain a supported action and thread ID")

    member = payload.get("member") or {}
    user = member.get("user") or payload.get("user") or {}
    message = payload.get("message") or {}
    return SlackEventRequest(
        thread_id=thread_id,
        action_id=action_id,
        user_id=str(user.get("id", "")),
        channel_id=str(payload.get("channel_id", "")),
        message_ts=str(message.get("id", "")),
        feedback=str(data.get("feedback", "")),
        event_id=str(payload.get("id", "")),
    )


def is_discord_ping(payload: dict[str, Any]) -> bool:
    return payload.get("type") == 1