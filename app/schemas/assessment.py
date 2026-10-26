"""Assessment API schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AssessmentRead(BaseModel):
    """Persisted audit and reviewer output."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: str | None
    status: str
    question: str | None
    audit_report: dict[str, object] | None
    compliance_review: str | None
    senior_review: str | None
    created_at: datetime
    updated_at: datetime


class AssessmentList(BaseModel):
    items: list[AssessmentRead]
    limit: int
    offset: int
