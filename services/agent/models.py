from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

WorkflowStatus = Literal[
    "DISCOVERED", "SCRAPED", "AUDITED", "AWAITING_REVIEW",
    "REVISION_REQUESTED", "APPROVED", "GENERATED", "DEPLOYED", "FAILED",
]
ApprovalStatus = Literal["pending", "approved", "revision_requested", "rejected"]


class Prospect(BaseModel):
    prospect_id: str = Field(min_length=1, max_length=200)
    url: HttpUrl


class ScrapedAssets(BaseModel):
    screenshot_path: str | None = None
    assets: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class AuditReport(BaseModel):
    visual_score: float = Field(ge=0, le=10)
    mobile_readiness_score: float = Field(ge=0, le=10)
    critique_summary: list[str] = Field(default_factory=list)
    recommended_improvements: list[str] = Field(default_factory=list)


class DesignBrief(BaseModel):
    summary: str = ""
    improvements: list[str] = Field(default_factory=list)


class HumanFeedback(BaseModel):
    user_id: str = ""
    channel_id: str = ""
    message_ts: str = ""
    action: Literal["approve", "request_revision", "reject"]
    feedback: str = ""


class GeneratedCode(BaseModel):
    content: str
    preview_url: str | None = None


class ErrorMetadata(BaseModel):
    message: str
    retry_count: int = Field(default=0, ge=0)
    retryable: bool = False


class AgencyState(BaseModel):
    model_config = ConfigDict(extra="forbid")
    thread_id: str = ""
    prospect: Prospect | None = None
    raw_assets: ScrapedAssets = Field(default_factory=ScrapedAssets)
    audit_report: AuditReport | None = None
    design_brief: DesignBrief = Field(default_factory=DesignBrief)
    status: WorkflowStatus = "DISCOVERED"
    approval_status: ApprovalStatus = "pending"
    human_feedback: list[HumanFeedback] = Field(default_factory=list)
    generated_code: GeneratedCode | None = None
    error: ErrorMetadata | None = None


class AuditRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    prospect_id: str = Field(default="local-prospect", max_length=200)
    url: HttpUrl = "https://example.com"
    screenshot_path: str | None = None
    assets: list[str] = Field(default_factory=list)


class AuditResponse(BaseModel):
    thread_id: str
    status: WorkflowStatus


class SlackEventRequest(BaseModel):
    thread_id: str
    action_id: Literal["approve_audit", "request_revision", "reject_audit"]
    user_id: str
    channel_id: str
    message_ts: str
    feedback: str = ""
    event_id: str


class StateResponse(BaseModel):
    thread_id: str
    state: AgencyState