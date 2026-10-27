"""Request and response schemas for local retrieval."""

from pydantic import BaseModel, Field


class RagQueryRequest(BaseModel):
    question: str = Field(min_length=1, max_length=8_000)


class RagPassage(BaseModel):
    title: str
    content: str
    source: str
    uri: str | None = None


class RagQueryResponse(BaseModel):
    question: str
    passages: list[RagPassage]
    sources: list[dict[str, str]]


class RagStatusResponse(BaseModel):
    available: bool
    embedding_model: str
    index_available: bool
    metadata_available: bool
    error_code: str | None = None
