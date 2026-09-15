from __future__ import annotations

import os
from typing import Any

import httpx


class GitHubPagesDeployer:
    def __init__(self, token: str | None = None, owner: str | None = None, repo: str | None = None) -> None:
        self.token = token or os.getenv("GITHUB_TOKEN", "")
        self.owner = owner or os.getenv("GITHUB_OWNER", "")
        self.repo = repo or os.getenv("GITHUB_REPO", "")
        self.base_url = "https://api.github.com"

    async def deploy_index(self, html_content: str, branch: str = "main") -> dict[str, Any]:
        if not self.token or not self.owner or not self.repo:
            return {"status": "skipped", "preview_url": None, "message": "GitHub deployment credentials not configured."}

        async with httpx.AsyncClient(timeout=30.0, headers={"Authorization": f"token {self.token}", "Accept": "application/vnd.github+json"}) as client:
            response = await client.get(f"{self.base_url}/repos/{self.owner}/{self.repo}")
            if response.status_code != 200:
                return {"status": "error", "preview_url": None, "message": "Repository not found or inaccessible."}

            payload = {
                "message": "feat: deploy generated landing page",
                "content": __import__("base64").b64encode(html_content.encode("utf-8")).decode("utf-8"),
                "branch": branch,
            }
            path = "index.html"
            put_url = f"{self.base_url}/repos/{self.owner}/{self.repo}/contents/{path}"
            put_response = await client.put(put_url, json=payload)
            if put_response.status_code not in (200, 201):
                return {"status": "error", "preview_url": None, "message": put_response.text}

            preview_url = f"https://{self.owner}.github.io/{self.repo}/"
            return {"status": "deployed", "preview_url": preview_url, "message": "Deployment successful."}
