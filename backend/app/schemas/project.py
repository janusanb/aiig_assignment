"""Pydantic schemas for Project."""
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.project_manager import ProjectManagerResponse


class ProjectBase(BaseModel):
    """Base schema with common attributes."""
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None


class ProjectCreate(ProjectBase):
    """Schema for creating a new project."""
    manager_id: int | None = None
    manager_name: str | None = None


class ProjectUpdate(BaseModel):
    """Schema for updating a project."""
    name: str | None = None
    description: str | None = None
    manager_id: int | None = None


class ProjectResponse(ProjectBase):
    """Schema for project responses."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    manager_id: int
    created_at: datetime
    updated_at: datetime


class ProjectWithManager(ProjectResponse):
    """Schema including manager details."""
    manager: ProjectManagerResponse


class ProjectWithStats(ProjectWithManager):
    """Schema including deliverable statistics."""
    total_deliverables: int = 0
    pending_deliverables: int = 0
    overdue_deliverables: int = 0
    upcoming_7_days: int = 0


class ProjectSearchResult(BaseModel):
    """Schema for project search results."""
    id: int
    name: str
    manager_name: str
    deliverable_count: int
