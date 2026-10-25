"""Evidence-bound compliance review agent using the shared LLM client."""

import json
from collections.abc import Sequence

from openai import AsyncOpenAI

from app.core.config import Settings
from app.services.llm.base import BaseLLM
from app.services.llm.role_prompts import load_role_prompt


class ComplianceAgent(BaseLLM):
    """Analyze infrastructure against retrieved evidence without inventing sources."""

    def __init__(
        self,
        settings: Settings,
        timeout_seconds: float = 30.0,
        client: AsyncOpenAI | None = None,
    ) -> None:
        super().__init__(settings, timeout_seconds, client)

    async def review(
        self,
        infrastructure: str,
        sources: Sequence[dict[str, str]],
    ) -> str:
        """Return an evidence-bound assessment of supplied infrastructure."""
        source_context = json.dumps(list(sources), ensure_ascii=False)
        prompt = (
            "Review this infrastructure description against only the source passages below. "
            "For each finding, explain the evidence and use the source's supplied identifiers. "
            "If evidence is insufficient, say so.\n\n"
            f"Infrastructure:\n{infrastructure}\n\n"
            f"Source passages:\n{source_context}"
        )
        return await self.complete(
            prompt,
            system_prompt=load_role_prompt("compliance_role.md"),
        )
