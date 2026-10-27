"""Local query embedding model lifecycle."""

from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING

from app.core.errors import AppError

if TYPE_CHECKING:
    from sentence_transformers import SentenceTransformer


@lru_cache(maxsize=2)
def load_embedding_model(model_name: str) -> SentenceTransformer:
    """Load and cache the configured CPU embedding model."""
    try:
        from sentence_transformers import SentenceTransformer

        return SentenceTransformer(model_name, device="cpu")
    except (ImportError, OSError, RuntimeError, ValueError) as exc:
        raise AppError(
            503,
            "rag_embedding_unavailable",
            "The local guidance embedding model is unavailable.",
        ) from exc
