"""Terraform API schemas."""

from typing import Annotated

from pydantic import BaseModel, Field


class TerraformGenerateRequest(BaseModel):
    project_id: str = Field(min_length=1, max_length=36)
    requirements: str = Field(min_length=1, max_length=8_000)


class TerraformCodeRequest(BaseModel):
    project_id: str = Field(min_length=1, max_length=36)
    code: str = Field(min_length=1, max_length=100_000)


class TerraformRepairRequest(TerraformCodeRequest):
    errors: list[Annotated[str, Field(min_length=1, max_length=4_000)]] = Field(
        min_length=1, max_length=20
    )


class TerraformPlanRequest(TerraformCodeRequest):
    pass


class TerraformArtifact(BaseModel):
    status: str
    code: str
    executed: bool = False


class TerraformOperationResult(BaseModel):
    status: str
    operation_id: str
    summary: str
    exit_code: int | None
    output_truncated: bool = False
