"""Retrieval API schemas."""

from pydantic import BaseModel, Field


class RagQuery(BaseModel):
    query: str = Field(min_length=1, max_length=2_000)
    limit: int = Field(default=5, ge=1, le=20)


class RagPassage(BaseModel):
    score: float
    text: str
    chunk_id: str
    source_title: str
    source_url: str
    document_version: str
    document_date: str
    section_id: str


class RagQueryResponse(BaseModel):
    status: str
    results: list[RagPassage]


class RagStatus(BaseModel):
    status: str
    indexed_passages: int
    dimension: int | None
    embedding_model: str | None
