"""Vector search and metadata-to-passage formatting."""

from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING

import numpy as np

from app.core.errors import AppError
from app.services.rag.embedding import load_embedding_model
from app.services.rag.models import RetrievedPassage
from app.services.rag.store import is_string_dict, load_store

if TYPE_CHECKING:
    from pathlib import Path

logger = logging.getLogger(__name__)
RESULT_LIMIT = 3
MAX_PASSAGE_CHARACTERS = 4_000
MAX_BEST_PRACTICES = 3


class RagRetriever:
    """Embed a query, search FAISS, and format attributed guidance passages."""

    def __init__(
        self,
        embedding_model: str,
        index_path: Path,
        metadata_path: Path,
    ) -> None:
        self.embedding_model = embedding_model
        self.index_path = index_path
        self.metadata_path = metadata_path

    def retrieve(self, question: str) -> list[RetrievedPassage]:
        """Return the most relevant local guidance passages for a query."""
        if not self.index_path.is_file() or not self.metadata_path.is_file():
            raise AppError(
                503,
                "rag_store_unavailable",
                "The local guidance index or metadata file is unavailable.",
            )
        model = load_embedding_model(self.embedding_model)
        import faiss

        index, documents = load_store(str(self.index_path), str(self.metadata_path))
        try:
            encoded = model.encode(
                question,
                convert_to_numpy=True,
                normalize_embeddings=index.metric_type == faiss.METRIC_INNER_PRODUCT,
                show_progress_bar=False,
            )
        except (OSError, RuntimeError, ValueError) as exc:
            logger.error("The configured embedding model could not encode a query.")
            raise AppError(
                503,
                "rag_embedding_unavailable",
                "The local guidance embedding model could not process the request.",
            ) from exc

        vector = np.asarray(encoded, dtype=np.float32).reshape(1, -1)
        if vector.shape[1] != index.d:
            raise AppError(
                503,
                "rag_embedding_mismatch",
                "The local guidance index is incompatible with the configured embedding model.",
            )

        try:
            _, matches = index.search(vector, min(RESULT_LIMIT, index.ntotal))
        except (RuntimeError, ValueError) as exc:
            logger.error("The local guidance index search failed (%s).", type(exc).__name__)
            raise AppError(
                503,
                "rag_search_failed",
                "The local guidance index could not complete the search.",
            ) from exc

        passages: list[RetrievedPassage] = []
        for document_index in matches[0]:
            if document_index < 0:
                continue
            if document_index >= len(documents):
                raise AppError(
                    503,
                    "rag_metadata_mismatch",
                    "The local guidance index and metadata are incompatible.",
                )
            passages.append(_format_passage(documents[document_index], question))
        return passages


def _format_passage(document: dict[str, object], question: str) -> RetrievedPassage:
    data_value = document.get("data")
    if not is_string_dict(data_value):
        raise AppError(
            503,
            "rag_metadata_invalid",
            "A retrieved local guidance document has invalid metadata.",
        )
    data = data_value
    title = _string(data.get("document_title")) or _string(document.get("source_document"))
    rag_metadata = data.get("rag_metadata")
    rag_fields = rag_metadata if isinstance(rag_metadata, dict) else {}
    summary = _string(rag_fields.get("retrieval_summary")) or _string(
        data.get("abstract_or_summary")
    )
    source = data.get("source")
    source_fields = source if isinstance(source, dict) else {}
    source_name = _string(source_fields.get("source_name")) or title
    source_uri = _string(source_fields.get("source_uri"))

    content_parts = [value for value in (title, summary) if value]
    topics = _strings(data.get("topics"))
    topics.extend(_strings(rag_fields.get("canonical_topics")))
    if topics:
        content_parts.append(f"Topics: {', '.join(dict.fromkeys(topics))}")

    practices = _relevant_practices(data.get("best_practices"), question)
    if practices:
        content_parts.append("Relevant guidance:\n" + "\n".join(f"- {item}" for item in practices))

    content = "\n\n".join(content_parts)[:MAX_PASSAGE_CHARACTERS]
    if not content:
        raise AppError(
            503,
            "rag_metadata_invalid",
            "A retrieved local guidance document has no usable content.",
        )
    return RetrievedPassage(title, content, source_name, source_uri)


def _relevant_practices(value: object, question: str) -> list[str]:
    if not isinstance(value, list):
        return []

    query_tokens = _tokens(question)
    ranked: list[tuple[int, int, str]] = []
    for position, practice in enumerate(value):
        if not isinstance(practice, dict):
            continue
        fields = (
            "title",
            "category",
            "desired_outcome",
            "matching_text",
            "implementation_steps",
            "benefits",
        )
        text = " — ".join(item for field in fields for item in _strings(practice.get(field)))
        if text:
            ranked.append((len(query_tokens.intersection(_tokens(text))), -position, text))

    ranked.sort(reverse=True)
    return [text[:1_000] for score, _, text in ranked[:MAX_BEST_PRACTICES] if score > 0]


def _string(value: object) -> str:
    return value.strip() if isinstance(value, str) else ""


def _strings(value: object) -> list[str]:
    if isinstance(value, str):
        return [value.strip()] if value.strip() else []
    if isinstance(value, list):
        return [item.strip() for item in value if isinstance(item, str) and item.strip()]
    return []


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]{3,}", text.casefold()))
