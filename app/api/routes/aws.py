"""AWS identity endpoint."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings
from app.schemas.aws import AWSIdentityResponse
from app.services.aws_service import AWSService

router = APIRouter(prefix="/aws", tags=["aws"])


@router.get("/identity", response_model=AWSIdentityResponse)
def aws_identity(settings: Annotated[Settings, Depends(get_settings)]) -> AWSIdentityResponse:
    return AWSService(settings).identity()
