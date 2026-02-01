"""
AIIG Deliverables Tracker - Main Application

A web application for managing project deliverables at
Americas Infrastructure Investments Group (AIIG).
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.database import init_db
from app.api import api_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    init_db()
    from app.core.database import SessionLocal
    from app.models import Project

    db = SessionLocal()
    try:
        if db.query(Project).count() == 0:
            import seed as seed_module
            seed_module.seed_database()
    finally:
        db.close()

    yield
    pass


def create_app() -> FastAPI:
    """Application factory."""
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="""
## AIIG Deliverables Tracker API

This API provides endpoints for managing infrastructure project deliverables.

### Features
- **Projects**: Search and manage infrastructure projects
- **Deliverables**: Track upcoming obligations and deadlines
- **Project Managers**: Manage project manager assignments
- **File Upload**: Import deliverables from Excel files

### Core Use Cases
1. Search for a project and view its upcoming deliverables
2. Filter deliverables by date, project, or manager
3. Add new projects, deliverables, and managers
4. Upload Excel files to bulk import deliverables
        """,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix=settings.API_PREFIX)

    @app.get("/health", tags=["Health"])
    def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION
        }

    @app.get("/", tags=["Root"])
    def root():
        """Root endpoint with API information."""
        return {
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "docs": "/docs",
            "api": settings.API_PREFIX
        }

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
