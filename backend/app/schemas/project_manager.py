"""Pydantic schemas for ProjectManager."""
from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr


class ProjectManagerBase(BaseModel):
    """Base schema with common attributes."""
    name: str
    email: EmailStr | None = None


class ProjectManagerCreate(ProjectManagerBase):
    """Schema for creating a new project manager."""
    pass


class ProjectManagerUpdate(BaseModel):
    """Schema for updating a project manager."""
    name: str | None = None
    email: EmailStr | None = None


class ProjectManagerResponse(ProjectManagerBase):
    """Schema for project manager responses."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class ProjectManagerWithStats(ProjectManagerResponse):
    """Schema including project count statistics."""
    project_count: int = 0
    deliverable_count: int = 0
