from __future__ import annotations

import os
import base64
from typing import Any

import httpx


class GitHubPagesDeployer:
    def __init__(self, token: str | None = None, owner: str | None = None, repo: str | None = None, client: httpx.AsyncClient | None = None) -> None:
        self.token = token or os.getenv("GITHUB_TOKEN", "")
        self.owner = owner or os.getenv("GITHUB_OWNER", "")
        self.repo = repo or os.getenv("GITHUB_REPO", "")
        self.base_url = "https://api.github.com"
        self.client = client

    async def deploy_index(self, html_content: str, branch: str = "main", *, approval_status: str = "") -> dict[str, Any]:
        if approval_status != "approved":
            return {"status": "skipped", "preview_url": None, "message": "Deployment requires approval_status=approved."}
        if not self.token or not self.owner or not self.repo:
            return {"status": "skipped", "preview_url": None, "message": "GitHub deployment credentials not configured."}

        client_context = self.client or httpx.AsyncClient(timeout=30.0, headers={"Authorization": f"token {self.token}", "Accept": "application/vnd.github+json"})
        async with client_context if self.client is None else _ExistingClient(client_context) as client:
            response = await client.get(f"{self.base_url}/repos/{self.owner}/{self.repo}")
            if response.status_code != 200:
                return {"status": "error", "preview_url": None, "message": "Repository not found or inaccessible."}

            payload = {
                "message": "feat: deploy generated landing page",
                "content": base64.b64encode(html_content.encode("utf-8")).decode("utf-8"),
                "branch": branch,
            }
            path = "index.html"
            put_url = f"{self.base_url}/repos/{self.owner}/{self.repo}/contents/{path}"
            existing = await client.get(put_url, params={"ref": branch})
            if existing.status_code == 200:
                payload["sha"] = existing.json().get("sha")
            elif existing.status_code != 404:
                return {"status": "error", "preview_url": None, "message": existing.text}
            put_response = await client.put(put_url, json=payload)
            if put_response.status_code not in (200, 201):
                return {"status": "error", "preview_url": None, "message": put_response.text}

            preview_url = f"https://{self.owner}.github.io/{self.repo}/"
            result = put_response.json()
            return {"status": "deployed", "preview_url": preview_url, "commit_sha": result.get("commit", {}).get("sha"), "repository": f"{self.owner}/{self.repo}", "branch": branch, "message": "Deployment successful."}


class _ExistingClient:
    def __init__(self, client: httpx.AsyncClient) -> None:
        self.client = client

    async def __aenter__(self) -> httpx.AsyncClient:
        return self.client

    async def __aexit__(self, *args: Any) -> None:
        return None
