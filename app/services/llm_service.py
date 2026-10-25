"""Configurable NVIDIA provider adapter."""

import logging
from typing import Any

import httpx

from app.core.config import Settings
from app.core.errors import AppError

logger = logging.getLogger(__name__)


class LLMService:
    """Minimal model adapter enabled only for an explicitly selected API format."""

    def __init__(self, settings: Settings, timeout_seconds: float = 30.0) -> None:
        self.settings = settings
        self.timeout_seconds = timeout_seconds

    def _ensure_configured(self) -> None:
        if not (
            self.settings.nvidia_api_key
            and self.settings.nvidia_base_url
            and self.settings.nvidia_model
            and self.settings.nvidia_api_format
        ):
            raise AppError(
                503,
                "provider_not_configured",
                "NVIDIA inference is not configured. Set a verified endpoint, model, "
                "API key, and API format.",
            )
        if self.settings.nvidia_api_format != "openai-chat-completions":
            raise AppError(
                503,
                "provider_format_unsupported",
                "The configured NVIDIA API format is not supported by this adapter.",
            )

    async def complete(self, message: str, history: list[dict[str, str]]) -> str:
        """Request a completion using an explicitly opted-in compatible format."""
        self._ensure_configured()
        messages = [{"role": item["role"], "content": item["content"]} for item in history]
        messages.append({"role": "user", "content": message})
        payload = {"model": self.settings.nvidia_model, "messages": messages}

        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.post(
                    self.settings.nvidia_base_url,
                    headers={"Authorization": f"Bearer {self.settings.nvidia_api_key}"},
                    json=payload,
                )
        except httpx.TimeoutException as exc:
            raise AppError(504, "provider_timeout", "The inference provider timed out.") from exc
        except httpx.RequestError as exc:
            raise AppError(502, "provider_unavailable", "The inference provider is unavailable.") from exc

        if response.status_code == 401 or response.status_code == 403:
            raise AppError(502, "provider_auth_error", "The inference provider rejected its credentials.")
        if response.status_code == 429:
            raise AppError(503, "provider_rate_limited", "The inference provider is rate limiting requests.")
        if response.is_error:
            raise AppError(502, "provider_error", "The inference provider returned an error.")
        try:
            body: Any = response.json()
            content = body["choices"][0]["message"]["content"]
            if not isinstance(content, str) or not content.strip():
                raise ValueError("Missing completion content")
        except (ValueError, KeyError, IndexError, TypeError) as exc:
            logger.warning("Inference provider returned a malformed response.")
            raise AppError(502, "provider_invalid_response", "The inference provider response was invalid.") from exc
        return content
