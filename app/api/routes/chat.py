"""Chat completion endpoint."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.llm.compliance_agent import ComplianceAgent
from app.services.llm.orchestrator import workflow
from app.services.llm.senior_agent import SeniorAgent
from app.services.llm.terraform_agent import TerraformAgent
from app.services.rag_service import RagService

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(
    body: ChatRequest,
    settings: Annotated[Settings, Depends(get_settings)],
) -> ChatResponse:
    """Return the complete proposal and evidence review without executing actions."""
    history = [item.model_dump() for item in body.history]
    retrieval = RagService(settings).query(body.message)
    sources = [
        {
            "chunk_id": str(item["chunk_id"]),
            "text": str(item["text"]),
            "source_title": str(item["source_title"]),
            "source_url": str(item["source_url"]),
            "document_version": str(item["document_version"]),
            "document_date": str(item["document_date"]),
            "section_id": str(item["section_id"]),
        }
        for item in retrieval["results"]
    ]
    senior_agent = SeniorAgent(settings)
    terraform_agent = TerraformAgent(settings)
    compliance_agent = ComplianceAgent(settings)
    async with senior_agent, terraform_agent, compliance_agent:
        result = await workflow(
            senior_agent=senior_agent,
            terraform_agent=terraform_agent,
            compliance_agent=compliance_agent,
            requirements=body.message,
            sources=sources,
            history=history,
        )
    return ChatResponse(
        assistant_response=result["response"],
        terraform=result["terraform"],
        compliance=result["compliance"],
        proposed_actions=[],
        sources=sources,
        status="completed",
    )
