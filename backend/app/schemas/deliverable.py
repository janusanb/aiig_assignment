"""Pydantic schemas for Deliverable."""
from datetime import datetime, date
from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.models.deliverable import DeliverableStatus


class DeliverableBase(BaseModel):
    """Base schema with common attributes."""
    description: str = Field(..., min_length=1, max_length=500)
    due_date: date
    frequency: str = Field(..., pattern="^(M|Q|SA|A|OT)$")


class DeliverableCreate(DeliverableBase):
    """Schema for creating a new deliverable."""
    project_id: int | None = None
    project_name: str | None = None
    notes: str | None = None

    @field_validator("frequency")
    @classmethod
    def validate_frequency(cls, v: str) -> str:
        valid = {"M", "Q", "SA", "A", "OT"}
        if v.upper() not in valid:
            raise ValueError(f"Frequency must be one of: {valid}")
        return v.upper()


class DeliverableUpdate(BaseModel):
    """Schema for updating a deliverable."""
    description: str | None = None
    due_date: date | None = None
    frequency: str | None = None
    status: DeliverableStatus | None = None
    notes: str | None = None


class DeliverableResponse(DeliverableBase):
    """Schema for deliverable responses."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    status: DeliverableStatus
    notes: str | None
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime


class DeliverableWithProject(DeliverableResponse):
    """Schema including project details."""
    project_name: str
    manager_name: str
    frequency_display: str
    days_until_due: int
    is_overdue: bool


class DeliverableFilter(BaseModel):
    """Schema for filtering deliverables."""
    project_id: int | None = None
    project_name: str | None = None
    manager_id: int | None = None
    status: DeliverableStatus | None = None
    frequency: str | None = None
    due_before: date | None = None
    due_after: date | None = None
    include_completed: bool = False
    search: str | None = None


class UpcomingDeliverablesSummary(BaseModel):
    """Summary of upcoming deliverables."""
    total: int
    overdue: int
    due_today: int
    due_this_week: int
    due_this_month: int
