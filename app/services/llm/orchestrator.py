"""Coordinate Terraform, compliance, and response agents."""

import asyncio
from collections.abc import Sequence
from typing import TypedDict

from app.services.llm.compliance_agent import ComplianceAgent
from app.services.llm.senior_agent import SeniorAgent
from app.services.llm.terraform_agent import TerraformAgent


class WorkflowResult(TypedDict):
    """Structured output from the assistant workflow."""

    response: str
    terraform: str
    compliance: str


async def workflow(
    senior_agent: SeniorAgent,
    terraform_agent: TerraformAgent,
    compliance_agent: ComplianceAgent,
    requirements: str,
    sources: Sequence[dict[str, str]],
    history: list[dict[str, str]] | None = None,
) -> WorkflowResult:
    """Generate Terraform and assess evidence concurrently, then review and repair Terraform.

    The Terraform and compliance agents receive the same requirements concurrently.
    Terraform is a proposal only; this function never executes Terraform CLI commands.
    """
    terraform_result, compliance_result = await asyncio.gather(
        terraform_agent.generate(requirements),
        compliance_agent.review(requirements, sources),
    )
    review = await senior_agent.review_proposal(
        requirements=requirements,
        code=terraform_result,
        compliance=compliance_result,
        sources=sources,
        history=history,
    )
    repaired_terraform = await senior_agent.repair(terraform_result, [review])
    return {
        "response": review,
        "terraform": repaired_terraform,
        "compliance": compliance_result,
    }
