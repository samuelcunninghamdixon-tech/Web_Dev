from typing import Literal, Optional

from pydantic import BaseModel, Field


ApprovalStatus = Literal["pending", "approved", "revision_requested", "rejected"]


class AgencyState(BaseModel):
    prospect_id: str = Field(default="")
    url: str = Field(default="")
    raw_assets: dict = Field(default_factory=dict)
    audit_report: dict = Field(default_factory=dict)
    design_brief: dict = Field(default_factory=dict)
    approval_status: ApprovalStatus = Field(default="pending")
    human_feedback: list[str] = Field(default_factory=list)
    generated_code: Optional[str] = None
    preview_url: Optional[str] = None
