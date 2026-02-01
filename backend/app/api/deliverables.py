"""API routes for Deliverable operations."""
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import DeliverableStatus
from app.schemas import (
    DeliverableCreate,
    DeliverableUpdate,
    DeliverableResponse,
    DeliverableWithProject,
    DeliverableFilter,
    UpcomingDeliverablesSummary,
)
from app.services import DeliverableService
from app.services.deliverable_service import DuplicateDeliverableError

router = APIRouter(prefix="/deliverables", tags=["Deliverables"])


@router.get("", response_model=list[DeliverableWithProject])
def list_deliverables(
    include_completed: bool = Query(False, description="Include completed deliverables"),
    db: Session = Depends(get_db)
):
    """Get all deliverables."""
    service = DeliverableService(db)
    deliverables = service.get_all(include_completed=include_completed)
    return [service.to_response_dict(d) for d in deliverables]


@router.get("/upcoming", response_model=list[DeliverableWithProject])
def get_upcoming_deliverables(
    days: int = Query(30, ge=1, le=365, description="Number of days to look ahead"),
    project_id: int | None = Query(None, description="Filter by project ID"),
    manager_id: int | None = Query(None, description="Filter by manager ID"),
    include_overdue: bool = Query(
        False,
        description="When filtering by project_id, include overdue deliverables for that project",
    ),
    db: Session = Depends(get_db),
):
    """Get deliverables due within the specified number of days.
    When include_overdue is True and project_id is set, overdue items for that project are included.
    """
    service = DeliverableService(db)
    deliverables = service.get_upcoming(
        days=days,
        project_id=project_id,
        manager_id=manager_id,
        include_overdue=include_overdue,
    )
    return [service.to_response_dict(d) for d in deliverables]


@router.get("/overdue", response_model=list[DeliverableWithProject])
def get_overdue_deliverables(
    project_id: int | None = Query(None, description="Filter by project ID"),
    manager_id: int | None = Query(None, description="Filter by manager ID"),
    db: Session = Depends(get_db)
):
    """Get all overdue deliverables."""
    service = DeliverableService(db)
    deliverables = service.get_overdue(
        project_id=project_id,
        manager_id=manager_id
    )
    return [service.to_response_dict(d) for d in deliverables]


@router.get("/summary", response_model=UpcomingDeliverablesSummary)
def get_deliverables_summary(
    project_id: int | None = Query(None, description="Filter by project ID"),
    manager_id: int | None = Query(None, description="Filter by manager ID"),
    db: Session = Depends(get_db)
):
    """Get summary statistics for deliverables."""
    service = DeliverableService(db)
    return service.get_summary(
        project_id=project_id,
        manager_id=manager_id
    )


@router.post("/filter", response_model=list[DeliverableWithProject])
def filter_deliverables(
    filters: DeliverableFilter,
    db: Session = Depends(get_db)
):
    """Filter deliverables based on multiple criteria."""
    service = DeliverableService(db)
    deliverables = service.filter(filters)
    return [service.to_response_dict(d) for d in deliverables]


@router.get("/{deliverable_id}", response_model=DeliverableWithProject)
def get_deliverable(deliverable_id: int, db: Session = Depends(get_db)):
    """Get a specific deliverable by ID."""
    service = DeliverableService(db)
    deliverable = service.get_by_id(deliverable_id)
    if not deliverable:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deliverable with ID {deliverable_id} not found"
        )
    return service.to_response_dict(deliverable)


@router.post("", response_model=DeliverableWithProject, status_code=status.HTTP_201_CREATED)
def create_deliverable(data: DeliverableCreate, db: Session = Depends(get_db)):
    """Create a new deliverable."""
    service = DeliverableService(db)
    try:
        deliverable = service.create(data)
        return service.to_response_dict(deliverable)
    except DuplicateDeliverableError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{deliverable_id}", response_model=DeliverableWithProject)
def update_deliverable(
    deliverable_id: int,
    data: DeliverableUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing deliverable."""
    service = DeliverableService(db)
    deliverable = service.update(deliverable_id, data)
    if not deliverable:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deliverable with ID {deliverable_id} not found"
        )
    return service.to_response_dict(deliverable)


@router.post("/{deliverable_id}/complete", response_model=DeliverableWithProject)
def mark_deliverable_complete(deliverable_id: int, db: Session = Depends(get_db)):
    """Mark a deliverable as completed."""
    service = DeliverableService(db)
    deliverable = service.mark_complete(deliverable_id)
    if not deliverable:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deliverable with ID {deliverable_id} not found"
        )
    return service.to_response_dict(deliverable)


@router.delete("/{deliverable_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_deliverable(deliverable_id: int, db: Session = Depends(get_db)):
    """Delete a deliverable."""
    service = DeliverableService(db)
    if not service.delete(deliverable_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deliverable with ID {deliverable_id} not found"
        )
