"""Knowledge retrieval endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings
from app.schemas.rag import RagQuery, RagQueryResponse, RagStatus
from app.services.rag_service import RagService

router = APIRouter(prefix="/rag", tags=["retrieval"])


@router.get("/status", response_model=RagStatus)
def rag_status(settings: Annotated[Settings, Depends(get_settings)]) -> RagStatus:
    return RagService(settings).status()


@router.post("/query", response_model=RagQueryResponse)
def rag_query(
    body: RagQuery,
    settings: Annotated[Settings, Depends(get_settings)],
) -> RagQueryResponse:
    return RagService(settings).query(body.query, body.limit)
