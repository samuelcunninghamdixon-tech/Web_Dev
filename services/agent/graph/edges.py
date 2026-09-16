from __future__ import annotations

from typing import Any


def _value(state: dict[str, Any] | Any, key: str) -> Any:
    if isinstance(state, dict):
        return state.get(key)
    return getattr(state, key, None)


def route_after_audit(state: dict[str, Any] | Any) -> str:
    return "slack_prompt" if _value(state, "status") == "AUDITED" else "failed"


def route_after_slack(state: dict[str, Any] | Any) -> str:
    if _value(state, "approval_status") == "approved":
        return "codegen"
    if _value(state, "approval_status") == "revision_requested":
        return "brief_revision"
    return "end"


def route_after_revision(state: dict[str, Any] | Any) -> str:
    return "slack_prompt" if _value(state, "status") == "AWAITING_REVIEW" else "failed"
