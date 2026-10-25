"""Chat API schemas."""

from typing import Any

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str = Field(pattern="^(user|assistant)$")
    content: str = Field(min_length=1, max_length=4_000)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=8_000)
    project_id: str | None = Field(default=None, max_length=36)
    history: list[ChatMessage] = Field(default_factory=list, max_length=20)
    region: str | None = Field(default=None, min_length=3, max_length=32)
    services: list[str] = Field(default_factory=list, max_length=30)
    prowler_args: list[str] = Field(default_factory=list, max_length=50)


class ChatResponse(BaseModel):
    assistant_response: str
    prowler_summary: str
    compliance: str
    sources: list[dict[str, str]]
    operation_id: str
    region: str
    findings_count: int
    findings: list[dict[str, Any]]
    status: str
