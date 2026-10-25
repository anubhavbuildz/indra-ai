"""Shared settings-backed OpenAI-compatible asynchronous client."""

import json
import logging
from typing import TYPE_CHECKING, Self, cast

from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AsyncOpenAI,
    AuthenticationError,
    RateLimitError,
)
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionToolUnionParam

from app.core.config import Settings
from app.core.errors import AppError

if TYPE_CHECKING:
    from openai.types.chat import ChatCompletion

logger = logging.getLogger(__name__)


class BaseLLM:
    """Shared provider configuration, OpenAI client, and safe completion handling."""

    def __init__(
        self,
        settings: Settings,
        timeout_seconds: float = 30.0,
        client: AsyncOpenAI | None = None,
    ) -> None:
        self.settings = settings
        self.timeout_seconds = timeout_seconds
        self._client = client

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

    @property
    def client(self) -> AsyncOpenAI:
        """Return the configured provider client, creating it only when invoked."""
        self._ensure_configured()
        if self._client is None:
            self._client = AsyncOpenAI(
                api_key=self.settings.nvidia_api_key,
                base_url=self.settings.nvidia_base_url,
                timeout=self.timeout_seconds,
                max_retries=0,
            )
        return self._client

    async def complete(
        self,
        message: str,
        history: list[dict[str, str]] | None = None,
        *,
        system_prompt: str | None = None,
        model: str | None = None,
    ) -> str:
        """Send a bounded conversation through the shared client and return assistant text."""
        messages: list[ChatCompletionMessageParam] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        for item in history or []:
            role = item.get("role")
            content = item.get("content")
            if role not in {"user", "assistant"} or not isinstance(content, str):
                raise AppError(422, "invalid_conversation", "Conversation history is invalid.")
            messages.append(cast(ChatCompletionMessageParam, {"role": role, "content": content}))
        messages.append(
            {
                "role": "user",
                "content": [{"type": "text", "text": message}],
            }
        )

        try:
            response: ChatCompletion = await self.client.chat.completions.create(
                model=model or self.settings.nvidia_model,
                messages=messages,
                temperature=0.6,
                max_completion_tokens=8192,
            )
        except APITimeoutError as exc:
            raise AppError(504, "provider_timeout", "The inference provider timed out.") from exc
        except AuthenticationError as exc:
            raise AppError(
                502, "provider_auth_error", "The inference provider rejected its credentials."
            ) from exc
        except RateLimitError as exc:
            raise AppError(
                503,
                "provider_rate_limited",
                "The inference provider is rate limiting requests.",
            ) from exc
        except APIConnectionError as exc:
            raise AppError(
                502, "provider_unavailable", "The inference provider is unavailable."
            ) from exc
        except APIStatusError as exc:
            logger.warning("Inference provider returned status=%s.", exc.status_code)
            raise AppError(
                502, "provider_error", "The inference provider returned an error."
            ) from exc

        try:
            content = response.choices[0].message.content
        except (AttributeError, IndexError, TypeError) as exc:
            logger.warning("Inference provider returned a malformed response.")
            raise AppError(
                502, "provider_invalid_response", "The inference provider response was invalid."
            ) from exc
        if not isinstance(content, str) or not content.strip():
            logger.warning("Inference provider returned a response without text content.")
            raise AppError(
                502, "provider_invalid_response", "The inference provider response was invalid."
            )
        return content

    async def request_tool_arguments(
        self,
        message: str,
        tool: ChatCompletionToolUnionParam,
        tool_name: str,
    ) -> dict[str, object]:
        """Ask the provider for one structured function call and return its arguments."""
        try:
            response = await self.client.chat.completions.create(
                model=self.settings.nvidia_model,
                messages=[{"role": "user", "content": message}],
                temperature=0,
                max_completion_tokens=512,
                tools=[tool],
                tool_choice={"type": "function", "function": {"name": tool_name}},
            )
        except APITimeoutError as exc:
            raise AppError(504, "provider_timeout", "The inference provider timed out.") from exc
        except AuthenticationError as exc:
            raise AppError(
                502, "provider_auth_error", "The inference provider rejected its credentials."
            ) from exc
        except RateLimitError as exc:
            raise AppError(
                503, "provider_rate_limited", "The inference provider is rate limiting requests."
            ) from exc
        except APIConnectionError as exc:
            raise AppError(
                502, "provider_unavailable", "The inference provider is unavailable."
            ) from exc
        except APIStatusError as exc:
            logger.warning("Inference provider returned status=%s.", exc.status_code)
            raise AppError(
                502, "provider_error", "The inference provider returned an error."
            ) from exc

        try:
            tool_calls = response.choices[0].message.tool_calls
        except (AttributeError, IndexError, TypeError) as exc:
            raise AppError(
                502, "provider_invalid_response", "The inference provider response was invalid."
            ) from exc
        if not tool_calls or len(tool_calls) != 1 or tool_calls[0].type != "function":
            raise AppError(
                502, "provider_invalid_response", "The inference provider response was invalid."
            )
        function = tool_calls[0].function
        if function.name != tool_name:
            raise AppError(
                502, "provider_invalid_response", "The inference provider response was invalid."
            )
        try:
            arguments = json.loads(function.arguments)
        except json.JSONDecodeError as exc:
            raise AppError(
                502, "provider_invalid_response", "The inference provider response was invalid."
            ) from exc
        if not isinstance(arguments, dict):
            raise AppError(
                502, "provider_invalid_response", "The inference provider response was invalid."
            )
        return arguments

    async def close(self) -> None:
        """Close the shared async client if it was initialized."""
        if self._client is not None:
            await self._client.close()
            self._client = None

    async def __aenter__(self) -> Self:
        self._ensure_configured()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        await self.close()
