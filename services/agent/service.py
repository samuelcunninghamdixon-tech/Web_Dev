from __future__ import annotations

from uuid import uuid4

from .graph.nodes import brief_revision_node, codegen_node
from .graph.workflow import build_workflow
from .models import AgencyState, AuditReport, AuditRequest, GeneratedCode, HumanFeedback, SlackEventRequest
from .utils.persistence import CheckpointStore, InMemoryCheckpointStore
from .utils.slack import map_slack_action


class AgentService:
    def __init__(self, store: CheckpointStore | None = None, *, audit_provider=None, codegen_provider=None) -> None:
        self.store = store or InMemoryCheckpointStore()
        self.workflow = build_workflow(audit_provider, codegen_provider)

    async def start_audit(self, request: AuditRequest) -> AgencyState:
        thread_id = str(uuid4())
        state = AgencyState(
            thread_id=thread_id,
            prospect={"prospect_id": request.prospect_id, "url": str(request.url)},
            raw_assets={"screenshot_path": request.screenshot_path, "assets": request.assets},
        )
        result = await self.workflow.ainvoke(state.model_dump())
        saved = AgencyState.model_validate(result)
        await self.store.put(thread_id, saved.model_dump())
        return saved

    async def get_state(self, thread_id: str) -> AgencyState | None:
        raw = await self.store.get(thread_id)
        return AgencyState.model_validate(raw) if raw else None

    async def handle_slack_event(self, event: SlackEventRequest) -> tuple[AgencyState, bool]:
        if not await self.store.claim_event(event.event_id):
            state = await self.get_state(event.thread_id)
            if state is None:
                raise KeyError(event.thread_id)
            return state, False
        state = await self.get_state(event.thread_id)
        if state is None:
            raise KeyError(event.thread_id)
        if state.status != "AWAITING_REVIEW":
            return state, False
        feedback = map_slack_action(event)
        state.human_feedback.append(feedback)
        if feedback.action == "approve":
            state.approval_status = "approved"
            state.status = "APPROVED"
            update = await codegen_node(state.model_dump())
        elif feedback.action == "request_revision":
            state.approval_status = "revision_requested"
            state.status = "REVISION_REQUESTED"
            update = await brief_revision_node(state.model_dump())
        else:
            state.approval_status = "rejected"
            state.status = "FAILED"
            update = {}
        state = AgencyState.model_validate({**state.model_dump(), **update})
        await self.store.put(event.thread_id, state.model_dump())
        return state, True