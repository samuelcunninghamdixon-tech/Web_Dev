from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["codegen"])


@router.get("/state/{thread_id}")
async def state_lookup(thread_id: str) -> dict:
    return {"thread_id": thread_id, "status": "pending"}
