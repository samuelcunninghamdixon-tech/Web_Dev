from __future__ import annotations

from typing import Any

from langgraph.graph import END, StateGraph

from .edges import route_after_audit, route_after_slack
from .nodes import audit_node, brief_revision_node, codegen_node, human_review_node, slack_prompt_node
from .state import AgencyState


def build_workflow() -> StateGraph:
    workflow = StateGraph(AgencyState)
    workflow.add_node("audit", audit_node)
    workflow.add_node("slack_prompt", slack_prompt_node)
    workflow.add_node("human_review", human_review_node)
    workflow.add_node("brief_revision", brief_revision_node)
    workflow.add_node("codegen", codegen_node)

    workflow.set_entry_point("audit")
    workflow.add_conditional_edges(
        "audit",
        route_after_audit,
        {"slack_prompt": "slack_prompt"},
    )
    workflow.add_conditional_edges(
        "slack_prompt",
        route_after_slack,
        {"human_review": "human_review"},
    )
    workflow.add_edge("human_review", "brief_revision")
    workflow.add_edge("brief_revision", "codegen")
    workflow.add_edge("codegen", END)
    return workflow
