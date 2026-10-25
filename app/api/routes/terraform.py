"""Terraform proposal and plan-only endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings
from app.core.errors import AppError
from app.schemas.terraform import (
    TerraformArtifact,
    TerraformCodeRequest,
    TerraformGenerateRequest,
    TerraformOperationResult,
    TerraformRepairRequest,
)
from app.services.terraform_service import TerraformService

router = APIRouter(prefix="/terraform", tags=["terraform"])


@router.post("/generate", response_model=TerraformArtifact)
async def generate(
    body: TerraformGenerateRequest,
    settings: Annotated[Settings, Depends(get_settings)],
) -> TerraformArtifact:
    result = await TerraformService(settings).generate(body.project_id, body.requirements)
    return TerraformArtifact.model_validate(result)


@router.post("/repair")
async def repair(
    body: TerraformRepairRequest,
    settings: Annotated[Settings, Depends(get_settings)],
) -> TerraformArtifact:
    result = await TerraformService(settings).repair(body.project_id, body.code, body.errors)
    return TerraformArtifact.model_validate(result)


@router.post("/validate", response_model=TerraformOperationResult)
def validate(
    body: TerraformCodeRequest,
    settings: Annotated[Settings, Depends(get_settings)],
) -> TerraformOperationResult:
    result = TerraformService(settings).validate(body.project_id, body.code)
    return TerraformOperationResult.model_validate(result)


@router.post("/plan", response_model=TerraformOperationResult)
def plan(
    body: TerraformCodeRequest,
    settings: Annotated[Settings, Depends(get_settings)],
) -> TerraformOperationResult:
    result = TerraformService(settings).plan(body.project_id, body.code)
    return TerraformOperationResult.model_validate(result)


@router.post("/apply")
@router.post("/destroy")
def unsupported_mutation() -> None:
    raise AppError(
        501,
        "terraform_mutation_not_implemented",
        "Apply and destroy are disabled; no deployment action was performed.",
    )
