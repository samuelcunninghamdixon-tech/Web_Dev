from __future__ import annotations

import base64
import json
import os
import re
from pathlib import Path
from typing import Any, Awaitable, Callable

import httpx

from ..models import AuditReport

JsonRequester = Callable[[dict[str, Any]], Awaitable[dict[str, Any]]]


class OllamaClient:
    def __init__(
        self,
        base_url: str | None = None,
        *,
        timeout: float = 120.0,
        retries: int = 2,
        requester: JsonRequester | None = None,
    ) -> None:
        self.base_url = (base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")).rstrip("/")
        self.timeout = timeout
        self.retries = retries
        self._requester = requester

    async def _request(self, payload: dict[str, Any]) -> dict[str, Any]:
        if self._requester:
            return await self._requester(payload)
        last_error: Exception | None = None
        for attempt in range(self.retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(f"{self.base_url}/api/generate", json=payload)
                    response.raise_for_status()
                    return response.json()
            except (httpx.HTTPError, ValueError) as error:
                last_error = error
                if attempt == self.retries:
                    raise
        raise RuntimeError("Ollama request failed") from last_error

    async def _set_keep_alive(self, model: str, keep_alive: str = "300s") -> None:
        await self._request({"model": model, "keep_alive": keep_alive, "prompt": "ping", "stream": False})

    async def evaluate_website_vision(self, screenshot_path: str | Path) -> AuditReport:
        model = os.getenv("VISION_MODEL", "qwen2-vl:7b")
        await self._set_keep_alive(model, "300s")
        image = base64.b64encode(Path(screenshot_path).read_bytes()).decode("ascii")
        result = await self._request({
            "model": model,
            "prompt": "Return only JSON with visual_score, mobile_readiness_score, critique_summary, recommended_improvements.",
            "stream": False,
            "keep_alive": "300s",
            "images": [image],
        })
        return AuditReport.model_validate(self._parse_json_response(result.get("response", "")))

    @staticmethod
    def _parse_json_response(content: str) -> dict[str, Any]:
        cleaned = content.strip()
        fenced = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", cleaned, flags=re.DOTALL | re.IGNORECASE)
        if fenced:
            cleaned = fenced.group(1).strip()
        try:
            value = json.loads(cleaned)
        except json.JSONDecodeError:
            match = re.search(r"\{(?:[^{}]|\{[^{}]*\})*\}", cleaned, re.DOTALL)
            if not match:
                raise ValueError("Ollama response did not contain a JSON object")
            value = json.loads(match.group(0))
        if not isinstance(value, dict):
            raise ValueError("Ollama response JSON must be an object")
        return value
