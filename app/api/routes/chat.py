"""Chat completion endpoint."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.llm.orchestrator import scan_workflow

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(
    body: ChatRequest,
    settings: Annotated[Settings, Depends(get_settings)],
) -> ChatResponse:
    """Scan AWS, assess compliance evidence, and return a senior review."""
    history = [item.model_dump() for item in body.history]
    result = await scan_workflow(
        settings,
        body.message,
        history,
        region=body.region,
        services=body.services,
        prowler_args=body.prowler_args,
    )
    return ChatResponse(
        assistant_response=result["response"],
        prowler_summary=result["prowler_summary"],
        compliance=result["compliance"],
        sources=result["sources"],
        operation_id=str(result["operation_id"]),
        region=str(result["region"]),
        findings_count=int(result["findings_count"]),
        findings=result["findings"],
        status="completed",
    )
