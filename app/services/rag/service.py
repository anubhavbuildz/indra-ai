"""Application service for RAG querying and readiness."""

import asyncio

from app.core.config import Settings
from app.services.rag.models import RagStatus, RetrievedPassage
from app.services.rag.retrieval import RagRetriever
from app.services.rag.store import resolve_store_path


class RagService:
    """Coordinate local retrieval components for workflow and HTTP routes."""

    def __init__(self, settings: Settings) -> None:
        self.embedding_model = settings.embedding_model
        self.index_path = resolve_store_path(settings.faiss_index_path)
        self.metadata_path = resolve_store_path(settings.faiss_metadata_path)
        self.retriever = RagRetriever(
            self.embedding_model,
            self.index_path,
            self.metadata_path,
        )

    async def query(self, question: str) -> list[RetrievedPassage]:
        """Retrieve guidance without blocking the async request loop."""
        return await asyncio.to_thread(self.retriever.retrieve, question)

    def status(self) -> RagStatus:
        """Report configured artifact presence without importing FAISS or loading the embedder."""
        index_available = self.index_path.is_file()
        metadata_available = self.metadata_path.is_file()
        available = index_available and metadata_available
        return RagStatus(
            available=available,
            embedding_model=self.embedding_model,
            index_available=index_available,
            metadata_available=metadata_available,
            error_code=None if available else "rag_store_unavailable",
        )
