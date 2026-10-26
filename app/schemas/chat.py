"""Chat API schemas."""

from pydantic import BaseModel, Field

from app.schemas.audit_schema import AuditReport


class ChatMessage(BaseModel):
    role: str = Field(pattern="^(user|assistant)$")
    content: str = Field(min_length=1, max_length=4_000)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=8_000)
    project_id: str | None = Field(default=None, max_length=36)
    history: list[ChatMessage] = Field(default_factory=list, max_length=20)


class ChatResponse(BaseModel):
    cloud_agent_response: AuditReport
    compliance_agent_response: str
    senior_agent_response: str
    sources: list[dict[str, str]]
    operation_id: str
    status: str
