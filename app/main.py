"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.api.routes.health import router as health_router
from app.core.config import get_settings
from app.core.errors import register_error_handlers
from app.core.logging import configure_logging
from app.core.middleware import RequestContextMiddleware

settings = get_settings()
configure_logging(settings.debug)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Initialize the local database schema on startup."""
    from app.db.session import initialize_database

    initialize_database(settings)
    yield


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    debug=settings.debug,
    lifespan=lifespan,
    docs_url="/docs" if settings.app_env == "development" else None,
    redoc_url="/redoc" if settings.app_env == "development" else None,
)
register_error_handlers(app)
app.add_middleware(
    RequestContextMiddleware,
    max_body_bytes=settings.max_request_bytes,
)
app.include_router(health_router)
app.include_router(api_router, prefix=settings.api_v1_prefix)

if settings.cors_origin_list:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=False,
        allow_methods=["GET", "POST", "PATCH"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
    )


@app.get("/")
def root() -> dict[str, str]:
    """Provide a minimal service greeting."""
    return {"service": settings.app_name, "docs": "/docs" if settings.app_env == "development" else ""}
