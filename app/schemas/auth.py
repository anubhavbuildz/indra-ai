"""Authentication request and response schemas."""

from pydantic import BaseModel, Field, SecretStr


class LoginRequest(BaseModel):
    """Credentials for the environment-configured login account."""

    username: str = Field(min_length=1, max_length=128)
    password: SecretStr = Field(min_length=1, max_length=1024)


class LoginResponse(BaseModel):
    """Short-lived bearer access token response."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int
