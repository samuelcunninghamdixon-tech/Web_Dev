from fastapi import APIRouter, Request

from ..models import AuditRequest, AuditResponse
from ..service import AgentService

router = APIRouter(prefix="/api", tags=["audit"])
service = AgentService()


@router.post("/audit")
async def start_audit(request: AuditRequest | None = None) -> AuditResponse:
    state = await service.start_audit(request or AuditRequest())
    return AuditResponse(thread_id=state.thread_id, status=state.status)
