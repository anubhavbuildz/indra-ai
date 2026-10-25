"""Senior reviewer for Prowler and evidence-based compliance assessments."""

import json

from openai import AsyncOpenAI

from app.core.config import Settings
from app.core.errors import AppError
from app.services.llm.base import BaseLLM
from app.services.llm.role_prompts import load_role_prompt

SENIOR_MODEL = "nvidia/nemotron-3-super-120b-a12b"
MAX_REVIEW_INPUT_BYTES = 120_000


class SeniorAgent(BaseLLM):
    """Review the Prowler summary and compliance assessment as a final reviewer."""

    def __init__(
        self,
        settings: Settings,
        timeout_seconds: float = 60.0,
        client: AsyncOpenAI | None = None,
    ) -> None:
        super().__init__(settings, timeout_seconds, client)

    async def review_prowler(
        self,
        question: str,
        region: str,
        prowler_summary: str,
        compliance: str,
        sources: list[dict[str, str]],
        history: list[dict[str, str]] | None = None,
    ) -> str:
        """Cross-check both agent results without inventing evidence or actions."""
        prompt = (
            f"User question:\n{question}\n\nAWS region: {region}\n\n"
            f"Prowler agent assessment:\n<prowler_summary>\n{prowler_summary}\n"
            "</prowler_summary>\n\n"
            f"Compliance agent assessment:\n<compliance>\n{compliance}\n</compliance>\n\n"
            "Retrieved source metadata and passages:\n"
            f"<sources>\n{json.dumps(sources, ensure_ascii=False)}\n</sources>"
        )
        input_bytes = (
            len(prompt.encode("utf-8"))
            + len(load_role_prompt("senior_role.md").encode("utf-8"))
            + sum(len(item["content"].encode("utf-8")) for item in history or [])
        )
        if input_bytes > MAX_REVIEW_INPUT_BYTES:
            raise AppError(
                413,
                "prowler_report_too_large",
                "The Prowler review and conversation exceed the senior agent input limit.",
            )
        return await self.complete(
            prompt,
            history,
            system_prompt=load_role_prompt("senior_role.md"),
            model=SENIOR_MODEL,
        )
