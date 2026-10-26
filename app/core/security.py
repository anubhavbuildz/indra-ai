"""Environment-configured login and JWT access-token helpers."""

import hmac
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt

from app.core.config import Settings, get_settings
from app.core.errors import AppError
from app.schemas.auth import LoginRequest

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class Login:
    """Verify the configured login and issue a signed access token."""

    def __init__(self, data: LoginRequest | None, settings: Settings | None = None) -> None:
        self.data = data
        self.settings = settings or get_settings()

    def data_validation(self) -> bool:
        """Return whether the request matches the configured account."""
        if (
            self.data is None
            or not self.settings.auth_username
            or not self.settings.auth_password
            or not self.settings.jwt_secret_key
        ):
            return False

        username_matches = hmac.compare_digest(
            self.data.username.encode("utf-8"),
            self.settings.auth_username.encode("utf-8"),
        )
        password_matches = hmac.compare_digest(
            self.data.password.get_secret_value().encode("utf-8"),
            self.settings.auth_password.encode("utf-8"),
        )
        return username_matches and password_matches

    def _encode(self) -> str:
        """Issue a signed JWT after validating the configured credentials."""
        if not self.settings.auth_username or not self.settings.auth_password:
            raise AppError(
                503,
                "login_not_configured",
                "Login credentials are not configured.",
            )
        if not self.settings.jwt_secret_key:
            raise AppError(
                503,
                "token_signing_not_configured",
                "Token signing is not configured.",
            )
        if not self.data_validation():
            raise AppError(401, "invalid_credentials", "Username or password is incorrect.")

        issued_at = datetime.now(UTC)
        expires_at = issued_at + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        claims = {
            "sub": self.settings.auth_username,
            "iat": issued_at,
            "exp": expires_at,
        }
        return jwt.encode(claims, self.settings.jwt_secret_key, algorithm=ALGORITHM)


def verify_access_token(token: str, settings: Settings | None = None) -> dict[str, Any]:
    """Decode and validate a signed, unexpired access token."""
    configured_settings = settings or get_settings()
    if not configured_settings.jwt_secret_key:
        raise AppError(
            503,
            "token_signing_not_configured",
            "Token signing is not configured.",
        )
    try:
        claims = jwt.decode(
            token,
            configured_settings.jwt_secret_key,
            algorithms=[ALGORITHM],
            options={"require": ["exp", "iat", "sub"]},
        )
    except jwt.InvalidTokenError as exc:
        raise AppError(401, "invalid_token", "The access token is invalid or expired.") from exc

    if not isinstance(claims.get("sub"), str) or not claims["sub"]:
        raise AppError(401, "invalid_token", "The access token is invalid or expired.")
    return claims
