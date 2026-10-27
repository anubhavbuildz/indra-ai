"""Coordinate AWS audits and chat responses."""

from typing import TypedDict

from app.core.config import Settings
from app.schemas.audit_schema import AuditReport
from app.services.llm.cloud_agent import CloudAgent
from app.services.llm.compliance_agent import ComplianceAgent
from app.services.llm.senior_agent import SeniorAgent
from app.services.rag import RagService


class WorkflowResult(TypedDict):
    """The AWS tool result and sequential Compliance/Senior reviews."""

    cloud_agent_response: dict[str, object]
    compliance_agent_response: str
    senior_agent_response: str
    sources: list[dict[str, str]]


async def chat_workflow(
    settings: Settings,
    question: str,
    history: list[dict[str, str]] | None = None,
) -> WorkflowResult:
    """Run AWS tools, retrieve guidance, summarize with Compliance, then review with Senior."""
    rag_service = RagService(settings)
    async with (
        CloudAgent(settings) as cloud_agent,
        ComplianceAgent(settings) as compliance_agent,
        SeniorAgent(settings) as senior_agent,
    ):
        compliance_agent.ensure_configured()
        audit_report: AuditReport = await cloud_agent.run_audit(
            question=question,
            history=history,
        )
        retrieved_passages = await rag_service.query(question)
        compliance_response = await compliance_agent.review(
            question=question,
            audit_result=audit_report,
            history=history,
            retrieved_passages=retrieved_passages,
        )
        senior_response = await senior_agent.review(
            question=question,
            audit_report=audit_report,
            compliance_assessment=compliance_response,
            history=history,
        )
    return {
        "cloud_agent_response": audit_report.model_dump(),
        "compliance_agent_response": compliance_response,
        "senior_agent_response": senior_response,
        "sources": [passage.as_source() for passage in retrieved_passages],
    }
