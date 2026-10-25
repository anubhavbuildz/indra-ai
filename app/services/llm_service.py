"""Compatibility import for the shared LLM service."""

from openai import AsyncOpenAI

from app.core.config import Settings
from app.services.llm.base import BaseLLM


class LLMService(BaseLLM):
    """Backward-compatible shared LLM interface."""

    def __init__(
        self,
        settings: Settings,
        timeout_seconds: float = 30.0,
        client: AsyncOpenAI | None = None,
    ) -> None:
        super().__init__(settings, timeout_seconds, client)
