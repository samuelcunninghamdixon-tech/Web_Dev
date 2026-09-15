from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["audit"])


@router.post("/audit")
async def start_audit() -> dict:
    return {"status": "accepted", "message": "Audit workflow created."}
