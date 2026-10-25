"""Coordinate Prowler analysis, evidence-bound compliance, and senior review."""

import asyncio
import json
from collections.abc import Sequence
from contextlib import AsyncExitStack
from typing import TypedDict

from app.core.config import Settings
from app.services.llm.compliance_agent import ComplianceAgent
from app.services.llm.prowler_agent import ProwlerAgent
from app.services.llm.senior_agent import SeniorAgent
from app.services.rag_service import RagService


class ProwlerWorkflowResult(TypedDict):
    """Complete output of a Prowler scan and its three-agent review."""

    operation_id: str
    region: str
    findings_count: int
    findings: list[dict[str, object]]
    prowler_summary: str
    compliance: str
    response: str
    sources: list[dict[str, str]]


async def review_scan(
    prowler_agent: ProwlerAgent,
    compliance_agent: ComplianceAgent,
    senior_agent: SeniorAgent,
    findings: list[dict[str, object]],
    region: str,
    sources: Sequence[dict[str, str]],
    question: str,
    history: list[dict[str, str]] | None = None,
) -> tuple[str, str, str]:
    """Run both assessments concurrently, then pass them to the senior reviewer."""
    source_list = list(sources)
    scan_context = json.dumps(
        {
            "question": question,
            "region": region,
            "findings": findings,
        },
        ensure_ascii=False,
    )
    prowler_summary, compliance = await asyncio.gather(
        prowler_agent.review(query=scan_context, sources=source_list),
        compliance_agent.review(infrastructure=scan_context, sources=source_list),
    )
    response = await senior_agent.review_prowler(
        question=question,
        region=region,
        prowler_summary=prowler_summary,
        compliance=compliance,
        sources=source_list,
        history=history,
    )
    return prowler_summary, compliance, response


async def scan_workflow(
    settings: Settings,
    question: str | None = None,
    history: list[dict[str, str]] | None = None,
    *,
    region: str | None = None,
    services: list[str] | None = None,
    prowler_args: list[str] | None = None,
) -> ProwlerWorkflowResult:
    """Scan AWS, assess Prowler results against retrieved guidance, and review both."""
    prompt_question = question or "Summarize findings and assess them against security guidance."
    async with AsyncExitStack() as stack:
        prowler_agent = await stack.enter_async_context(ProwlerAgent(settings))
        compliance_agent = await stack.enter_async_context(ComplianceAgent(settings))
        senior_agent = await stack.enter_async_context(SeniorAgent(settings))
        scan = await prowler_agent.run_scan(
            region=region,
            services=services,
            prowler_args=prowler_args,
        )

        retrieval = RagService(settings).query(prompt_question)
        sources: Sequence[dict[str, object]] = retrieval["results"]
        source_metadata = [
            {
                key: str(source[key])
                for key in (
                    "chunk_id",
                    "text",
                    "source_title",
                    "source_url",
                    "document_version",
                    "document_date",
                    "section_id",
                )
            }
            for source in sources
        ]
        prowler_summary, compliance, response = await review_scan(
            prowler_agent=prowler_agent,
            compliance_agent=compliance_agent,
            senior_agent=senior_agent,
            findings=scan["findings"],
            region=scan["region"],
            sources=source_metadata,
            question=prompt_question,
            history=history,
        )

    return {
        **scan,
        "prowler_summary": prowler_summary,
        "compliance": compliance,
        "response": response,
        "sources": source_metadata,
    }
