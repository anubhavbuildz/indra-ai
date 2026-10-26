"""Versioned API router."""

from fastapi import APIRouter

from app.api.routes.assessments import router as assessments_router
from app.api.routes.auth import router as auth_router
from app.api.routes.aws import router as aws_router
from app.api.routes.chat import router as chat_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(assessments_router)
api_router.include_router(chat_router)
api_router.include_router(aws_router)
