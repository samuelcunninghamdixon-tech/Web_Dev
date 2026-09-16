from fastapi import APIRouter, Header, HTTPException, Request

from ..config import Settings
from ..models import SlackEventRequest
from ..utils.slack import verify_slack_signature
from .audit import service

router = APIRouter(prefix="/api", tags=["slack"])


@router.post("/slack-event")
async def receive_slack_event(
    event: SlackEventRequest,
    request: Request,
    x_slack_request_timestamp: str | None = Header(default=None),
    x_slack_signature: str | None = Header(default=None),
) -> dict:
    settings = Settings()
    if settings.slack_signing_secret and not verify_slack_signature(
        settings.slack_signing_secret,
        x_slack_request_timestamp or "",
        await request.body(),
        x_slack_signature or "",
    ):
        raise HTTPException(status_code=401, detail="invalid Slack signature")
    try:
        state, processed = await service.handle_slack_event(event)
    except KeyError as error:
        raise HTTPException(status_code=404, detail="workflow thread not found") from error
    return {"status": "processed" if processed else "duplicate", "thread_id": state.thread_id, "state": state.status}
