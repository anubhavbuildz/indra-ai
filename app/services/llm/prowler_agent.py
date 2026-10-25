"""Evidence-bound compliance review agent using the shared LLM client."""

import json
from collections.abc import Sequence

from openai import AsyncOpenAI

from app.core.config import Settings
from app.services.llm.base import BaseLLM
from app.services.llm.role_prompts import load_role_prompt
from app.tools.prowler.scanner import ScanResult, run_prowler_scan


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
        return await run_prowler_scan(
            self.settings,
            region=region,
            services=services,
            prowler_args=prowler_args,
        )

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
            "If evidence is insufficient, use your `run_scan` tool to fetch live telemetry.\n\n"
            f"query:\n{query}\n\n"
            f"Source passages:\n{source_context}"
        )
        return await self.complete(
            prompt,
            system_prompt=load_role_prompt("prowler_role.md"),
        )
