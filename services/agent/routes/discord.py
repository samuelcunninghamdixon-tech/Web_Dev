from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from ..config import Settings
from ..utils.discord import is_discord_ping, parse_discord_interaction, verify_discord_signature
from .audit import service

router = APIRouter(prefix="/api", tags=["discord"])


@router.post("/discord-interaction")
async def receive_discord_interaction(request: Request) -> dict:
    settings = Settings()
    raw_body = await request.body()
    signature = request.headers.get("X-Signature-Ed25519", "")
    timestamp = request.headers.get("X-Signature-Timestamp", "")
    if not verify_discord_signature(settings.discord_public_key, timestamp, raw_body, signature):
        raise HTTPException(status_code=401, detail="invalid Discord signature")

    try:
        payload = await request.json()
    except ValueError as error:
        raise HTTPException(status_code=400, detail="invalid JSON payload") from error
    if is_discord_ping(payload):
        return {"type": 1}

    try:
        event = parse_discord_interaction(payload)
        state, processed = await service.handle_slack_event(event)
    except (KeyError, ValueError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return {"type": 4, "data": {"content": f"Review {'processed' if processed else 'already processed'} for {state.thread_id}."}}