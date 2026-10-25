"""Prowler scan endpoint."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings
from app.schemas.prowler import ProwlerScanRequest, ProwlerScanResponse
from app.services.llm.orchestrator import scan_workflow

router = APIRouter(prefix="/prowler", tags=["prowler"])


@router.post("/scan", response_model=ProwlerScanResponse)
async def scan(
    settings: Annotated[Settings, Depends(get_settings)],
    body: ProwlerScanRequest | None = None,
) -> ProwlerScanResponse:
    request = body or ProwlerScanRequest()
    result = await scan_workflow(
        settings,
        region=request.region,
        services=request.services,
        prowler_args=request.prowler_args,
    )
    return ProwlerScanResponse(
        operation_id=str(result["operation_id"]),
        region=str(result["region"]),
        findings_count=int(result["findings_count"]),
        assistant_response=result["response"],
        prowler_summary=result["prowler_summary"],
        compliance=result["compliance"],
        sources=result["sources"],
        findings=result["findings"],
    )
