"""Process health routes."""

from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings

router = APIRouter(tags=["health"])


@router.get("/health")
def health(settings: Settings = Depends(get_settings)) -> dict[str, str]:
    """Report basic process health without inspecting paid external services."""
    return {"status": "ok", "service": settings.app_name, "version": "0.1.0"}


@router.get("/ready")
def ready(settings: Settings = Depends(get_settings)) -> dict[str, object]:
    """Report local configuration readiness without exposing secret values."""
    return {
        "status": "ready",
        "database_configured": bool(settings.database_url),
        "rag_index_configured": settings.faiss_index_path.exists()
        and settings.faiss_metadata_path.exists(),
    }

