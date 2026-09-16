from fastapi import APIRouter, HTTPException

from ..models import StateResponse
from .audit import service

router = APIRouter(prefix="/api", tags=["codegen"])


@router.get("/state/{thread_id}")
async def state_lookup(thread_id: str) -> dict:
    state = await service.get_state(thread_id)
    if state is None:
        raise HTTPException(status_code=404, detail="workflow thread not found")
    return StateResponse(thread_id=thread_id, state=state)
