"""Terraform-specific prompt behavior built on the shared LLM client."""

from openai import AsyncOpenAI

from app.core.config import Settings
from app.services.llm.base import BaseLLM
from app.services.llm.role_prompts import load_role_prompt


class TerraformAgent(BaseLLM):
    """Generate proposed Terraform through shared provider functionality."""

    def __init__(
        self,
        settings: Settings,
        timeout_seconds: float = 30.0,
        client: AsyncOpenAI | None = None,
    ) -> None:
        super().__init__(settings, timeout_seconds, client)

    async def generate(self, requirements: str) -> str:
        """Return a proposed Terraform configuration; never execute it."""
        return await self.complete(
            requirements,
            system_prompt=load_role_prompt("terraform_role.md"),
        )
