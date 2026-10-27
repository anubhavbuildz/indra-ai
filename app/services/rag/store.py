"""FAISS index and trusted local metadata loading."""

from __future__ import annotations

import logging
import pickle
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING, TypeGuard

from app.core.config import PROJECT_ROOT
from app.core.errors import AppError

if TYPE_CHECKING:
    import faiss

logger = logging.getLogger(__name__)


def resolve_store_path(path: Path) -> Path:
    """Resolve relative index paths from the application root."""
    return path if path.is_absolute() else PROJECT_ROOT / path


def is_string_dict(value: object) -> TypeGuard[dict[str, object]]:
    return isinstance(value, dict) and all(isinstance(key, str) for key in value)


def is_document_list(value: object) -> TypeGuard[list[dict[str, object]]]:
    return isinstance(value, list) and all(
        is_string_dict(document) and is_string_dict(document.get("data")) for document in value
    )


@lru_cache(maxsize=4)
def load_store(
    index_path: str,
    metadata_path: str,
) -> tuple[faiss.Index, list[dict[str, object]]]:
    """Load and validate a trusted local FAISS index and its paired pickle metadata."""
    import faiss

    index_file = Path(index_path)
    metadata_file = Path(metadata_path)
    if not index_file.is_file() or not metadata_file.is_file():
        raise AppError(
            503,
            "rag_store_unavailable",
            "The local guidance index or metadata file is unavailable.",
        )

    try:
        index = faiss.read_index(str(index_file))
    except (OSError, RuntimeError) as exc:
        logger.error("The local guidance index could not be loaded (%s).", type(exc).__name__)
        raise AppError(
            503,
            "rag_index_invalid",
            "The local guidance index could not be loaded.",
        ) from exc

    try:
        # Only locally generated metadata is read; the API never accepts pickle uploads.
        with metadata_file.open("rb") as file:
            documents = pickle.load(file)
    except (
        AttributeError,
        EOFError,
        ImportError,
        OSError,
        pickle.UnpicklingError,
        TypeError,
        ValueError,
    ) as exc:
        logger.error("The local guidance metadata could not be loaded (%s).", type(exc).__name__)
        raise AppError(
            503,
            "rag_metadata_invalid",
            "The local guidance metadata could not be loaded.",
        ) from exc

    if not is_document_list(documents) or len(documents) != index.ntotal or index.ntotal == 0:
        raise AppError(
            503,
            "rag_metadata_mismatch",
            "The local guidance index and metadata are incompatible.",
        )
    return index, documents
