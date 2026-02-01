"""API routes module."""
from fastapi import APIRouter
from app.api.managers import router as managers_router
from app.api.projects import router as projects_router
from app.api.deliverables import router as deliverables_router
from app.api.upload import router as upload_router

api_router = APIRouter()

api_router.include_router(managers_router)
api_router.include_router(projects_router)
api_router.include_router(deliverables_router)
api_router.include_router(upload_router)

__all__ = ["api_router"]
