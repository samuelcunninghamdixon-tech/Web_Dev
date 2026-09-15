from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["slack"])


@router.post("/slack-event")
async def receive_slack_event() -> dict:
    return {"status": "received"}
