from __future__ import annotations

from typing import Any, Awaitable, Callable

from langgraph.graph import END, StateGraph

from ..models import AgencyState, AuditReport, GeneratedCode
from .edges import route_after_audit, route_after_revision, route_after_slack
from .nodes import audit_node, brief_revision_node, codegen_node, failed_node, slack_prompt_node

AuditProvider = Callable[[AgencyState], Awaitable[AuditReport]]
CodegenProvider = Callable[[AgencyState], Awaitable[GeneratedCode]]


def build_workflow(
    audit_provider: AuditProvider | None = None,
    codegen_provider: CodegenProvider | None = None,
) -> Any:
    async def audit_step(state: dict[str, Any]) -> dict[str, Any]:
        return await audit_node(state, audit_provider)

    async def codegen_step(state: dict[str, Any]) -> dict[str, Any]:
        return await codegen_node(state, codegen_provider)

    workflow = StateGraph(AgencyState)
    workflow.add_node("audit", audit_step)
    workflow.add_node("slack_prompt", slack_prompt_node)
    workflow.add_node("brief_revision", brief_revision_node)
    workflow.add_node("codegen", codegen_step)
    workflow.add_node("failed", failed_node)
    workflow.set_entry_point("audit")
    workflow.add_conditional_edges("audit", route_after_audit, {"slack_prompt": "slack_prompt", "failed": "failed"})
    workflow.add_conditional_edges("slack_prompt", route_after_slack, {"codegen": "codegen", "brief_revision": "brief_revision", "end": END})
    workflow.add_conditional_edges("brief_revision", route_after_revision, {"slack_prompt": "slack_prompt", "failed": "failed"})
    workflow.add_edge("codegen", END)
    workflow.add_edge("failed", END)
    return workflow.compile()
