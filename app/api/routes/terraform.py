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
)
from app.services.terraform_service import TerraformService

router = APIRouter(prefix="/terraform", tags=["terraform"])


@router.post("/generate", response_model=TerraformArtifact)
async def generate(
    body: TerraformGenerateRequest,
    settings: Annotated[Settings, Depends(get_settings)],
) -> TerraformArtifact:
    return await TerraformService(settings).generate(body.project_id, body.requirements)


@router.post("/validate", response_model=TerraformOperationResult)
def validate(
    body: TerraformCodeRequest,
    settings: Annotated[Settings, Depends(get_settings)],
) -> TerraformOperationResult:
    return TerraformService(settings).validate(body.project_id, body.code)


@router.post("/plan", response_model=TerraformOperationResult)
def plan(
    body: TerraformCodeRequest,
    settings: Annotated[Settings, Depends(get_settings)],
) -> TerraformOperationResult:
    return TerraformService(settings).plan(body.project_id, body.code)


@router.post("/apply")
@router.post("/destroy")
def unsupported_mutation() -> None:
    raise AppError(
        501,
        "terraform_mutation_not_implemented",
        "Apply and destroy are disabled; no deployment action was performed.",
    )
