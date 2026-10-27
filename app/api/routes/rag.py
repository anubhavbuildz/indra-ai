"""Local retrieval API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings
from app.schemas.rag import RagPassage, RagQueryRequest, RagQueryResponse, RagStatusResponse
from app.services.rag import RagService

router = APIRouter(prefix="/rag", tags=["retrieval"])


@router.get("/status", response_model=RagStatusResponse)
def rag_status(settings: Annotated[Settings, Depends(get_settings)]) -> RagStatusResponse:
    """Report local index availability without loading the embedding model."""
    status = RagService(settings).status()
    return RagStatusResponse(
        available=status.available,
        embedding_model=status.embedding_model,
        index_available=status.index_available,
        metadata_available=status.metadata_available,
        error_code=status.error_code,
    )


@router.post("/query", response_model=RagQueryResponse)
async def rag_query(
    body: RagQueryRequest,
    settings: Annotated[Settings, Depends(get_settings)],
) -> RagQueryResponse:
    """Retrieve locally indexed guidance passages and their citations."""
    passages = await RagService(settings).query(body.question)
    return RagQueryResponse(
        question=body.question,
        passages=[
            RagPassage(
                title=passage.title,
                content=passage.content,
                source=passage.source_name,
                uri=passage.source_uri or None,
            )
            for passage in passages
        ],
        sources=[passage.as_source() for passage in passages],
    )
