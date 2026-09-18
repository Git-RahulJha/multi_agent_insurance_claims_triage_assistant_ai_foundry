from typing import Literal

from pydantic import BaseModel, Field


class Evidence(BaseModel):
    source: str
    details: object


class CoverageAnalysis(BaseModel):
    claim_id: str
    policy_number: str
    coverage_status: Literal[
        "covered",
        "not_covered",
        "unknown",
    ]

    claim_type_covered: bool | None
    within_policy_period: bool | None
    amount_within_limit: bool | None

    anomaly_flags: list[str] = Field(default_factory=list)
    investigation_required: bool
    evidence: list[Evidence] = Field(default_factory=list)
    reasoning: str


class IntakeValidation(BaseModel):
    claim_id: str
    valid: bool
    missing_fields: list[str] = Field(default_factory=list)
    validation_errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    requires_manual_review: bool
    evidence: list[Evidence] = Field(default_factory=list)
    reasoning: str

class AdjusterBriefing(BaseModel):
    claim_id: str
    summary: str
    key_findings: list[str] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)
    investigation_reasons: list[str] = Field(default_factory=list)
    recommended_action: Literal[
        "approve",
        "reject",
        "request_more_information",
        "manual_review",
    ]
    supporting_evidence: list[Evidence] = Field(default_factory=list)
    reasoning: str

class AgentError(BaseModel):
    agent: str
    error_type: str
    message: str
    recoverable: bool = False