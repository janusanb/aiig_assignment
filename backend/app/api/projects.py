"""API routes for Project operations."""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectWithManager,
    ProjectWithStats,
    ProjectSearchResult,
    DeliverableWithProject,
)
from app.services import ProjectService, DeliverableService

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get("", response_model=list[ProjectWithStats])
def list_projects(db: Session = Depends(get_db)):
    """Get all projects with their statistics."""
    service = ProjectService(db)
    return service.get_all_with_stats()


@router.get("/search", response_model=list[ProjectSearchResult])
def search_projects(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(10, ge=1, le=50, description="Maximum results"),
    db: Session = Depends(get_db)
):
    """
    Search projects by name.
    Returns matching projects with manager name and deliverable count.
    """
    service = ProjectService(db)
    return service.get_search_results(q, limit)


@router.get("/{project_id}", response_model=ProjectWithStats)
def get_project(project_id: int, db: Session = Depends(get_db)):
    """Get a specific project by ID with statistics."""
    service = ProjectService(db)
    result = service.get_with_stats(project_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {project_id} not found"
        )
    return result


@router.get("/{project_id}/deliverables", response_model=list[DeliverableWithProject])
def get_project_deliverables(
    project_id: int,
    include_completed: bool = Query(False, description="Include completed deliverables"),
    limit: int | None = Query(None, ge=1, le=100, description="Maximum results"),
    db: Session = Depends(get_db)
):
    """Get all deliverables for a specific project."""
    project_service = ProjectService(db)
    deliverable_service = DeliverableService(db)

    project = project_service.get_by_id(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {project_id} not found"
        )

    deliverables = deliverable_service.get_by_project(
        project_id,
        include_completed=include_completed,
        limit=limit
    )

    return [deliverable_service.to_response_dict(d) for d in deliverables]


@router.post("", response_model=ProjectWithManager, status_code=status.HTTP_201_CREATED)
def create_project(data: ProjectCreate, db: Session = Depends(get_db)):
    """Create a new project."""
    service = ProjectService(db)

    existing = service.get_by_name(data.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Project with name '{data.name}' already exists"
        )

    try:
        return service.create(data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{project_id}", response_model=ProjectWithManager)
def update_project(
    project_id: int,
    data: ProjectUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing project."""
    service = ProjectService(db)
    result = service.update(project_id, data)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {project_id} not found"
        )
    return result


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    """Delete a project and all its deliverables."""
    service = ProjectService(db)
    if not service.delete(project_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {project_id} not found"
        )
