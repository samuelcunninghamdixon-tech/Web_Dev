import base64

import httpx
from fastapi.testclient import TestClient

from services.codegen.app import StaticHtmlModel, create_app
from services.codegen.deployer import GitHubPagesDeployer
from services.codegen.generator import generate_landing_page
from services.codegen.validator import ValidationResult, validate_required_content


def test_generator_escapes_text_and_rejects_unapproved_logo() -> None:
    page = generate_landing_page(
        {"business_name": "<script>alert(1)</script>", "headline": 'Say "hello"'},
        {"logo_url": "https://evil.example/logo.png"},
    )

    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in page
    assert "https://evil.example/logo.png" not in page
    assert "<script>" not in page


def test_generation_requires_approval_and_returns_typed_validation() -> None:
    client = TestClient(create_app(model_client=StaticHtmlModel(), validator=lambda html: ValidationResult(True)))

    assert client.post("/generate", json={"approval_status": "pending"}).status_code == 403
    response = client.post("/generate", json={"approval_status": "approved"})

    assert response.status_code == 200
    assert response.json()["validation"]["valid"] is True
    assert response.json()["prompt_version"] == "v1"


def test_required_content_helper_catches_missing_sections() -> None:
    assert "Missing required content: h1" in validate_required_content("<main></main>")


def test_deployment_requires_approval_without_credentials() -> None:
    client = TestClient(create_app(deployer=GitHubPagesDeployer(token="", owner="", repo="")))

    response = client.post("/deploy", json={"approval_status": "pending", "html": "<html></html>"})

    assert response.status_code == 403


def test_deployment_sends_existing_file_sha_to_github() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.url.path.endswith("/contents/index.html") and request.method == "GET":
            return httpx.Response(200, json={"sha": "old-sha"})
        if request.method == "PUT":
            return httpx.Response(200, json={"commit": {"sha": "new-sha"}})
        return httpx.Response(200, json={})

    github_client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    deployer = GitHubPagesDeployer(token="token", owner="owner", repo="repo", client=github_client)

    import asyncio
    result = asyncio.run(deployer.deploy_index("<html></html>", approval_status="approved"))

    put_request = next(request for request in requests if request.method == "PUT")
    assert result["commit_sha"] == "new-sha"
    import json
    payload = json.loads(put_request.content)
    assert payload["sha"] == "old-sha"
    assert base64.b64decode(payload["content"]) == b"<html></html>"
