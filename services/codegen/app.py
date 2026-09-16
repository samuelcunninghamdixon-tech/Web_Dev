from __future__ import annotations

import os
from typing import Any, Callable, Protocol

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field

try:
    from .deployer import GitHubPagesDeployer
    from .generator import generate_landing_page
    from .validator import ValidationResult, validate_generated_page
except ImportError:
    from deployer import GitHubPagesDeployer
    from generator import generate_landing_page
    from validator import ValidationResult, validate_generated_page


class HtmlModelClient(Protocol):
    async def generate(self, design_brief: dict[str, Any], assets: dict[str, Any]) -> str: ...


class GenerateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    approval_status: str
    design_brief: dict[str, Any] = Field(default_factory=dict)
    assets: dict[str, Any] = Field(default_factory=dict)
    approved_external_links: list[str] = Field(default_factory=list)


class HtmlRequest(BaseModel):
    html: str


class ValidationResponse(BaseModel):
    valid: bool
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class GenerationResponse(BaseModel):
    html: str
    model: str
    prompt_version: str
    validation: ValidationResponse
    warnings: list[str] = Field(default_factory=list)


class DeploymentRequest(BaseModel):
    approval_status: str
    html: str
    branch: str = "main"


class StaticHtmlModel:
    async def generate(self, design_brief: dict[str, Any], assets: dict[str, Any]) -> str:
        return generate_landing_page(design_brief, assets)


class OllamaHtmlModel:
    def __init__(self, base_url: str | None = None, model: str | None = None) -> None:
        self.base_url = (base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")).rstrip("/")
        self.model = model or os.getenv("CODEGEN_MODEL", "llama3.1:8b")

    async def generate(self, design_brief: dict[str, Any], assets: dict[str, Any]) -> str:
        prompt = (
            "Return only a complete HTML document. Do not include markdown fences, scripts, secrets, or API keys. "
            f"Design brief: {design_brief}\nApproved assets and links: {assets}"
        )
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(f"{self.base_url}/api/generate", json={"model": self.model, "prompt": prompt, "stream": False})
            response.raise_for_status()
            content = response.json().get("response", "").strip()
        if content.startswith("```") or "<html" not in content.lower():
            raise ValueError("Ollama returned content that is not a complete HTML document")
        return content


def _validation_response(result: ValidationResult) -> ValidationResponse:
    return ValidationResponse.model_validate(result.__dict__)


def create_app(*, model_client: HtmlModelClient | None = None, deployer: GitHubPagesDeployer | None = None, validator: Callable[[str], ValidationResult] | None = None) -> FastAPI:
    app = FastAPI(title="Code Generation Service")
    selected_model = model_client or OllamaHtmlModel()
    selected_deployer = deployer or GitHubPagesDeployer()
    selected_validator = validator or validate_generated_page

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/generate", response_model=GenerationResponse)
    async def generate(request: GenerateRequest) -> GenerationResponse:
        if request.approval_status != "approved":
            raise HTTPException(status_code=403, detail="Generation requires approval_status=approved.")
        assets = {**request.assets, "allowed_urls": request.approved_external_links}
        html = await selected_model.generate(request.design_brief, assets)
        validation = _validation_response(selected_validator(html))
        return GenerationResponse(
            html=html,
            model=os.getenv("CODEGEN_MODEL", "static-template"),
            prompt_version=os.getenv("CODEGEN_PROMPT_VERSION", "v1"),
            validation=validation,
            warnings=validation.warnings,
        )

    @app.post("/validate", response_model=ValidationResponse)
    def validate(request: HtmlRequest) -> ValidationResponse:
        return _validation_response(selected_validator(request.html))

    @app.post("/deploy")
    async def deploy(request: DeploymentRequest) -> dict[str, Any]:
        result = await selected_deployer.deploy_index(request.html, request.branch, approval_status=request.approval_status)
        if result["status"] == "skipped" and request.approval_status != "approved":
            raise HTTPException(status_code=403, detail=result["message"])
        return result

    return app


app = create_app()