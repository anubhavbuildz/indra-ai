"""Versioned API router."""

from fastapi import APIRouter

from app.api.routes.aws import router as aws_router
from app.api.routes.chat import router as chat_router
from app.api.routes.projects import router as projects_router
from app.api.routes.rag import router as rag_router

api_router = APIRouter()
api_router.include_router(chat_router)
api_router.include_router(aws_router)
api_router.include_router(projects_router)
api_router.include_router(rag_router)
