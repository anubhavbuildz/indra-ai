"""Versioned API router."""

from fastapi import APIRouter, Depends

from app.api.dependencies import require_access_token
from app.api.routes.assessments import router as assessments_router
from app.api.routes.auth import router as auth_router
from app.api.routes.aws import router as aws_router
from app.api.routes.chat import router as chat_router
from app.api.routes.rag import router as rag_router

api_router = APIRouter()
api_router.include_router(auth_router)
protected_route_dependencies = [Depends(require_access_token)]
api_router.include_router(assessments_router, dependencies=protected_route_dependencies)
api_router.include_router(chat_router, dependencies=protected_route_dependencies)
api_router.include_router(rag_router, dependencies=protected_route_dependencies)
api_router.include_router(aws_router, dependencies=protected_route_dependencies)
