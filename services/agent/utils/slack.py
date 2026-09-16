from __future__ import annotations

import hashlib
import hmac
import time
from typing import Literal

from ..models import HumanFeedback, SlackEventRequest

Action = Literal["approve", "request_revision", "reject"]
ACTION_MAP: dict[str, Action] = {
    "approve_audit": "approve",
    "request_revision": "request_revision",
    "reject_audit": "reject",
}


def verify_slack_signature(signing_secret: str, timestamp: str, raw_body: bytes, signature: str, *, now: float | None = None, max_age: int = 300) -> bool:
    try:
        timestamp_value = int(timestamp)
    except ValueError:
        return False
    current = time.time() if now is None else now
    if abs(current - timestamp_value) > max_age:
        return False
    base = b"v0:" + timestamp.encode("ascii") + b":" + raw_body
    expected = "v0=" + hmac.new(signing_secret.encode(), base, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


def map_slack_action(event: SlackEventRequest) -> HumanFeedback:
    return HumanFeedback(
        user_id=event.user_id,
        channel_id=event.channel_id,
        message_ts=event.message_ts,
        action=ACTION_MAP[event.action_id],
        feedback=event.feedback,
    )