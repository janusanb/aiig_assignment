"""API routes for Project Manager operations."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas import (
    ProjectManagerCreate,
    ProjectManagerUpdate,
    ProjectManagerResponse,
    ProjectManagerWithStats,
)
from app.services import ProjectManagerService

router = APIRouter(prefix="/managers", tags=["Project Managers"])


@router.get("", response_model=list[ProjectManagerWithStats])
def list_managers(db: Session = Depends(get_db)):
    """Get all project managers with their statistics."""
    service = ProjectManagerService(db)
    return service.get_all_with_stats()


@router.get("/{manager_id}", response_model=ProjectManagerWithStats)
def get_manager(manager_id: int, db: Session = Depends(get_db)):
    """Get a specific project manager by ID."""
    service = ProjectManagerService(db)
    result = service.get_with_stats(manager_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project manager with ID {manager_id} not found"
        )
    return result


@router.post("", response_model=ProjectManagerResponse, status_code=status.HTTP_201_CREATED)
def create_manager(data: ProjectManagerCreate, db: Session = Depends(get_db)):
    """Create a new project manager."""
    service = ProjectManagerService(db)

    existing = service.get_by_name(data.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Project manager with name '{data.name}' already exists"
        )

    return service.create(data)


@router.put("/{manager_id}", response_model=ProjectManagerResponse)
def update_manager(
    manager_id: int,
    data: ProjectManagerUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing project manager."""
    service = ProjectManagerService(db)
    result = service.update(manager_id, data)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project manager with ID {manager_id} not found"
        )
    return result


@router.delete("/{manager_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_manager(manager_id: int, db: Session = Depends(get_db)):
    """Delete a project manager."""
    service = ProjectManagerService(db)
    if not service.delete(manager_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project manager with ID {manager_id} not found"
        )
