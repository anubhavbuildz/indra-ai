"""Assessment API schemas."""

from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, field_serializer


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

    @field_serializer("created_at", "updated_at")
    def serialize_timestamp(self, value: datetime) -> str:
        """Return persisted UTC timestamps with an explicit UTC offset."""
        normalized = value.replace(tzinfo=UTC) if value.tzinfo is None else value.astimezone(UTC)
        return normalized.isoformat().replace("+00:00", "Z")


class AssessmentList(BaseModel):
    items: list[AssessmentRead]
    limit: int
    offset: int
