"""Evidence-bound compliance review agent using the shared LLM client."""

import json
from collections.abc import Sequence

from openai import AsyncOpenAI

from app.core.config import Settings
from app.core.errors import AppError
from app.services.llm.base import BaseLLM
from app.services.llm.role_prompts import load_role_prompt
from app.tools.prowler.scanner import ScanArguments, Scanner, ScanResult
from app.tools.prowler.schema import prowler_scan_tool


class ProwlerAgent(BaseLLM):
    """Analyze infrastructure against retrieved evidence without inventing sources."""

    def __init__(
        self,
        settings: Settings,
        timeout_seconds: float = 30.0,
        client: AsyncOpenAI | None = None,
    ) -> None:
        super().__init__(settings, timeout_seconds, client)

    async def run_scan(
        self,
        region: str | None = None,
        services: list[str] | None = None,
        prowler_args: list[str] | None = None,
    ) -> ScanResult:
        """Run the Prowler CLI tool for the current request."""
        return await Scanner(self.settings).run_scan(
            region=region,
            services=services,
            prowler_args=prowler_args,
        )

    async def choose_scan_arguments(
        self,
        question: str,
        *,
        region: str | None = None,
        services: list[str] | None = None,
        prowler_args: list[str] | None = None,
    ) -> ScanArguments:
        """Let the model select extra scan scope while preserving caller-specified values."""
        request = {
            "question": question,
            "requested_region": region,
            "requested_services": services or [],
            "requested_cli_arguments": prowler_args or [],
            "default_region": self.settings.aws_region,
        }
        arguments = await self.request_tool_arguments(
            "Choose scan arguments for the user request below. Use the "
            "select_scan_arguments function only. "
            "Preserve any explicitly requested region, services, and CLI arguments; when they "
            "are omitted, choose only useful read-only Prowler scan options. Return arguments "
            "as separate CLI tokens, never as a command or shell expression. Request:\n"
            + json.dumps(request, ensure_ascii=False),
            prowler_scan_tool[0],
            "select_scan_arguments",
        )
        allowed = {"region", "services", "prowler_args"}
        if set(arguments) - allowed:
            raise AppError(
                502, "provider_invalid_response", "The inference provider response was invalid."
            )

        selected_region = arguments.get("region")
        selected_services = arguments.get("services", [])
        selected_args = arguments.get("prowler_args", [])
        if selected_region is not None and not isinstance(selected_region, str):
            raise AppError(
                502, "provider_invalid_response", "The inference provider response was invalid."
            )
        if not isinstance(selected_services, list) or any(
            not isinstance(item, str) for item in selected_services
        ):
            raise AppError(
                502, "provider_invalid_response", "The inference provider response was invalid."
            )
        if not isinstance(selected_args, list) or any(
            not isinstance(item, str) for item in selected_args
        ):
            raise AppError(
                502, "provider_invalid_response", "The inference provider response was invalid."
            )

        return {
            "region": region or selected_region,
            "services": services or selected_services,
            "prowler_args": prowler_args or selected_args,
        }

    async def review(
        self,
        query: str,
        sources: Sequence[dict[str, str]],
    ) -> str:
        """Return an evidence-bound assessment of supplied infrastructure."""
        source_context = json.dumps(list(sources), ensure_ascii=False)
        prompt = (
            "Review this infrastructure description against only the source passages below. "
            "For each finding, explain the evidence and use the source's supplied identifiers. "
            "If evidence is insufficient, state what the supplied scan and sources "
            "do not establish.\n\n"
            f"query:\n{query}\n\n"
            f"Source passages:\n{source_context}"
        )
        return await self.complete(
            prompt,
            system_prompt=load_role_prompt("prowler_role.md"),
        )
