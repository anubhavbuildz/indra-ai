"""Deterministic local feature-hash embeddings used as a non-semantic baseline."""

import hashlib
import math
import re

from app.core.errors import AppError

EMBEDDING_DIMENSION = 384
EMBEDDING_MODEL_ID = "local-feature-hash-v1"
_TOKEN_PATTERN = re.compile(r"[a-z0-9]+")


class EmbeddingService:
    """Create consistent normalized vectors without downloading a model."""

    def __init__(self, model_id: str = EMBEDDING_MODEL_ID) -> None:
        if model_id != EMBEDDING_MODEL_ID:
            raise AppError(
                503,
                "embedding_model_unsupported",
                "The configured embedding model is not implemented by this build.",
            )
        self.model_id = model_id

    @staticmethod
    def preprocess(text: str) -> str:
        """Normalize text identically for passages and queries."""
        return " ".join(_TOKEN_PATTERN.findall(text.lower()))

    def embed(self, text: str) -> list[float]:
        normalized = self.preprocess(text)
        vector = [0.0] * EMBEDDING_DIMENSION
        for token in normalized.split():
            digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
            value = int.from_bytes(digest, "big")
            index = value % EMBEDDING_DIMENSION
            vector[index] += 1.0 if value & (1 << 63) else -1.0
        magnitude = math.sqrt(sum(component * component for component in vector))
        if magnitude:
            vector = [component / magnitude for component in vector]
        return vector
