from __future__ import annotations

from typing import Any


def route_after_audit(state: dict[str, Any]) -> str:
    return "slack_prompt"


def route_after_slack(state: dict[str, Any]) -> str:
    return "human_review"
