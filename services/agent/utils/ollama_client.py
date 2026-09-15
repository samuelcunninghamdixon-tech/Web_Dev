from __future__ import annotations

import json
import os
import re
from typing import Any

import httpx


class OllamaClient:
    def __init__(self, base_url: str | None = None) -> None:
        self.base_url = (base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")).rstrip("/")

    async def _request(self, payload: dict[str, Any]) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(f"{self.base_url}/api/generate", json=payload)
            response.raise_for_status()
            return response.json()

    async def _set_keep_alive(self, model: str, keep_alive: str = "300s") -> None:
        payload = {"model": model, "keep_alive": keep_alive, "prompt": "ping"}
        await self._request(payload)

    async def evaluate_website_vision(self, screenshot_path: str) -> dict[str, Any]:
        model = os.getenv("VISION_MODEL", "qwen2-vl:7b")
        await self._set_keep_alive(model, "300s")

        with open(screenshot_path, "rb") as image_file:
            data = image_file.read()

        payload = {
            "model": model,
            "prompt": "Return only JSON with visual_score, mobile_readiness_score, critique_summary, recommended_improvements.",
            "stream": False,
            "images": [data.hex()],
        }

        result = await self._request(payload)
        content = result.get("response", "")
        return self._parse_json_response(content)

    def _parse_json_response(self, content: str) -> dict[str, Any]:
        cleaned = content.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
            cleaned = re.sub(r"\s*```$", "", cleaned)

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", cleaned, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(0))
                except json.JSONDecodeError:
                    pass
            return {
                "visual_score": 5,
                "mobile_readiness_score": 5,
                "critique_summary": ["Unable to parse model response."],
                "recommended_improvements": ["Review screenshot manually."],
            }
