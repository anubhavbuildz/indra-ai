"""Senior Terraform repair agent using the configured NVIDIA-compatible provider."""

import json
from collections.abc import Sequence

from openai import AsyncOpenAI

from app.core.config import Settings
from app.services.llm.base import BaseLLM
from app.services.llm.role_prompts import load_role_prompt

SENIOR_MODEL = "nvidia/nemotron-3-super-120b-a12b"


class SeniorAgent(BaseLLM):
    """Repair Terraform source based on explicit diagnostics without executing it."""

    def __init__(
        self,
        settings: Settings,
        timeout_seconds: float = 60.0,
        client: AsyncOpenAI | None = None,
    ) -> None:
        super().__init__(settings, timeout_seconds, client)

    async def review_proposal(
        self,
        requirements: str,
        code: str,
        compliance: str,
        sources: Sequence[dict[str, str]],
        history: list[dict[str, str]] | None = None,
    ) -> str:
        """Review the Terraform and compliance results for the user-facing response."""
        prompt = (
            f"Requirements:\n{requirements}\n\n"
            f"Proposed Terraform (review only; do not rewrite):\n"
            f"<terraform>\n{code}\n</terraform>\n\n"
            f"Evidence-bound compliance assessment:\n"
            f"<compliance>\n{compliance}\n</compliance>\n\n"
            f"Available source metadata:\n"
            f"{json.dumps(list(sources), ensure_ascii=False)}"
        )
        return await self.complete(
            prompt,
            history,
            system_prompt=load_role_prompt("senior_role.md", "Review System Prompt"),
            model=SENIOR_MODEL,
        )

    async def repair(self, code: str, errors: Sequence[str]) -> str:
        """Return revised HCL based on caller-supplied validation diagnostics."""
        prompt = (
            "Repair the Terraform source using the diagnostics below. Preserve its "
            "intended architecture where possible. If a diagnostic is ambiguous, "
            "make the smallest safe correction.\n\n"
            f"Terraform source:\n<terraform>\n{code}\n</terraform>\n\n"
            f"Diagnostics:\n<diagnostics>\n{chr(10).join(errors)}\n</diagnostics>"
        )
        result = await self.complete(
            prompt,
            system_prompt=load_role_prompt("senior_role.md", "Repair System Prompt"),
            model=SENIOR_MODEL,
        )
        result = result.strip()
        if result.startswith("```") and result.endswith("```"):
            first_line_end = result.find("\n")
            if first_line_end >= 0 and result[:first_line_end].strip().lower() in {
                "```",
                "```terraform",
                "```hcl",
            }:
                return result[first_line_end + 1 : -3].strip()
        return result
