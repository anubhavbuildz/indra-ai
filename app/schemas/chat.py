"""Chat API schemas."""

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str = Field(pattern="^(user|assistant)$")
    content: str = Field(min_length=1, max_length=4_000)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=8_000)
    project_id: str | None = Field(default=None, max_length=36)
    history: list[ChatMessage] = Field(default_factory=list, max_length=20)


class ChatResponse(BaseModel):
    assistant_response: str
    proposed_actions: list[dict[str, str]]
    sources: list[dict[str, str]]
    status: str
