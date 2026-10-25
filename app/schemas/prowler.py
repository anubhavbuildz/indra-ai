"""Prowler scan API schemas."""

from typing import Any

from pydantic import BaseModel, Field


class ProwlerScanRequest(BaseModel):
    """Optional request scope for the Prowler CLI tool."""

    region: str | None = Field(default=None, min_length=3, max_length=32)
    services: list[str] = Field(default_factory=list, max_length=30)
    prowler_args: list[str] = Field(default_factory=list, max_length=50)


class ProwlerScanResponse(BaseModel):
    operation_id: str
    status: str = "completed"
    region: str
    findings_count: int = Field(ge=0)
    assistant_response: str
    prowler_summary: str
    compliance: str
    sources: list[dict[str, str]]
    findings: list[dict[str, Any]]
