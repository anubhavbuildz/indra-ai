"""Shared API dependencies."""

from typing import Annotated, Any

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import Settings, get_settings
from app.core.errors import AppError
from app.core.security import verify_access_token

bearer_scheme = HTTPBearer(auto_error=False)


def require_access_token(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(bearer_scheme),
    ],
    settings: Annotated[Settings, Depends(get_settings)],
) -> dict[str, Any]:
    """Require a valid JWT bearer token for protected API routes."""
    if credentials is None:
        raise AppError(
            401,
            "authentication_required",
            "A valid Bearer access token is required.",
        )
    return verify_access_token(credentials.credentials, settings)
