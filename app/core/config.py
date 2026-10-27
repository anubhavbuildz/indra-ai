"""Typed application settings loaded from environment and optional .env file."""

from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Runtime configuration; integration credentials remain optional."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    app_name: str = Field(default="Indra API", validation_alias="APP_NAME")
    app_env: str = Field(default="development", validation_alias="APP_ENV")
    debug: bool = Field(default=False, validation_alias="DEBUG")
    api_v1_prefix: str = Field(default="/api/v1", validation_alias="API_V1_PREFIX")
    database_url: str = Field(default="sqlite:///./data/indra.db", validation_alias="DATABASE_URL")
    auth_username: str = Field(default="", validation_alias="AUTH_USERNAME", repr=False)
    auth_password: str = Field(default="", validation_alias="AUTH_PASSWORD", repr=False)
    jwt_secret_key: str = Field(default="", validation_alias="JWT_SECRET_KEY", repr=False)
    nvidia_base_url: str = Field(
        default="https://api.tokenfactory.nebius.com/v1",
        validation_alias="NVIDIA_BASE_URL",
    )
    nvidia_api_key: str = Field(default="", validation_alias="NVIDIA_API_KEY", repr=False)
    nvidia_model: str = Field(
        default="nvidia/Nemotron-3_5-Lightning",
        validation_alias="NVIDIA_MODEL",
    )
    nvidia_api_format: str = Field(
        default="openai-chat-completions",
        validation_alias="NVIDIA_API_FORMAT",
    )
    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        validation_alias="EMBEDDING_MODEL",
    )
    faiss_index_path: Path = Field(
        default=Path("faiss_store/security.index"),
        validation_alias="FAISS_INDEX_PATH",
    )
    faiss_metadata_path: Path = Field(
        default=Path("faiss_store/security.pkl"),
        validation_alias="FAISS_METADATA_PATH",
    )
    aws_region: str = Field(default="us-east-1", validation_alias="AWS_REGION")
    cors_origins: str = Field(default="", validation_alias="CORS_ORIGINS")
    max_request_bytes: int = Field(default=1_048_576, ge=1_024, le=10_485_760)

    @field_validator("jwt_secret_key")
    @classmethod
    def validate_jwt_secret_key(cls, value: str) -> str:
        """Require a sufficiently strong key when JWT login is configured."""
        if value and len(value.encode("utf-8")) < 32:
            raise ValueError("JWT_SECRET_KEY must contain at least 32 bytes.")
        return value

    @property
    def cors_origin_list(self) -> list[str]:
        """Return configured CORS origins without empty entries."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def integrations_ready(self) -> dict[str, bool]:
        """Return non-secret integration configuration state."""
        return {
            "nvidia": bool(
                self.nvidia_api_key
                and self.nvidia_base_url
                and self.nvidia_model
                and self.nvidia_api_format
            ),
            "aws": True,
        }


@lru_cache
def get_settings() -> Settings:
    """Return cached settings for dependency injection."""
    return Settings()
