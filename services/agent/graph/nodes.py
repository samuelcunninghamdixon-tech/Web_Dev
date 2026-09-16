from __future__ import annotations

from typing import Any, Awaitable, Callable

from ..models import AgencyState, AuditReport, DesignBrief, GeneratedCode


async def audit_node(state: dict[str, Any], audit_provider: Callable[[AgencyState], Awaitable[AuditReport]] | None = None) -> dict[str, Any]:
    typed = AgencyState.model_validate(state)
    report = await audit_provider(typed) if audit_provider else AuditReport(
        visual_score=0, mobile_readiness_score=0, critique_summary=["Audit provider not configured"],
    )
    brief = DesignBrief(summary="Website audit ready for human review.", improvements=report.recommended_improvements)
    return {"audit_report": report.model_dump(), "status": "AUDITED", "design_brief": brief.model_dump()}


async def slack_prompt_node(state: dict[str, Any]) -> dict[str, Any]:
    return {"status": "AWAITING_REVIEW"}


async def brief_revision_node(state: dict[str, Any]) -> dict[str, Any]:
    typed = AgencyState.model_validate(state)
    feedback = typed.human_feedback[-1].feedback if typed.human_feedback else ""
    brief = typed.design_brief.model_copy(update={"summary": f"{typed.design_brief.summary} {feedback}".strip()})
    return {"design_brief": brief.model_dump(), "status": "AWAITING_REVIEW", "approval_status": "pending"}


async def codegen_node(state: dict[str, Any], codegen_provider: Callable[[AgencyState], Awaitable[GeneratedCode]] | None = None) -> dict[str, Any]:
    typed = AgencyState.model_validate(state)
    if typed.approval_status != "approved":
        raise PermissionError("code generation requires explicit approval")
    generated = await codegen_provider(typed) if codegen_provider else GeneratedCode(content="")
    return {"generated_code": generated.model_dump(), "status": "GENERATED"}


async def failed_node(state: dict[str, Any]) -> dict[str, Any]:
    return {"status": "FAILED"}
