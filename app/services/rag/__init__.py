"""Local FAISS retrieval service."""

from app.services.rag.models import RagStatus, RetrievedPassage
from app.services.rag.service import RagService

__all__ = ["RagService", "RagStatus", "RetrievedPassage"]
