"""Typed contract for the AWS auditor results consumed by LLM agents."""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

AuditSeverity = Literal["CRITICAL", "HIGH", "MEDIUM", "LOW"]
AuditService = Literal["s3", "iam", "ec2", "vpc", "rds", "cloudtrail", "guardduty"]


class AuditFinding(BaseModel):
    """One resource finding or service-level audit error."""

    model_config = ConfigDict(extra="allow")

    service: str
    region: str
    check_id: str | None = None
    resource: str | None = None
    severity: AuditSeverity | None = None
    title: str | None = None
    issue: str | None = None
    remediation: str | None = None
    error: str | None = None
    evidence: dict[str, Any] | None = None


class AuditReport(BaseModel):
    """Summary and findings returned by the selected AWS audit tools."""

    model_config = ConfigDict(extra="forbid")

    audited_regions: list[str]
    audited_services: list[AuditService] = Field(default_factory=list)
    total_issues: int = Field(ge=0)
    critical_count: int = Field(ge=0)
    high_count: int = Field(ge=0)
    medium_count: int = Field(ge=0)
    low_count: int = Field(ge=0)
    findings: list[AuditFinding]


AUDIT_REPORT_JSON_SCHEMA = AuditReport.model_json_schema()
