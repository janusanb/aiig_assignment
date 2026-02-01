"""Deliverable model for storing project deliverable information."""
from datetime import datetime
from enum import Enum

from app.core.datetime_utils import utc_today
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Date, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.core.database import Base


class FrequencyType(str, Enum):
    """Frequency types for deliverables."""
    MONTHLY = "M"
    QUARTERLY = "Q"
    SEMI_ANNUAL = "SA"
    ANNUAL = "A"
    ONE_TIME = "OT"


class DeliverableStatus(str, Enum):
    """Status tracking for deliverables."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    OVERDUE = "overdue"


class Deliverable(Base):
    """
    Represents a deliverable obligation for a project.
    
    Tracks due dates, frequency, and completion status
    to help senior management monitor compliance.
    """
    __tablename__ = "deliverables"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    description = Column(String(500), nullable=False)
    due_date = Column(Date, nullable=False, index=True)
    frequency = Column(String(10), nullable=False)
    status = Column(
        SQLEnum(DeliverableStatus), 
        default=DeliverableStatus.PENDING, 
        nullable=False
    )
    notes = Column(String(1000), nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project = relationship("Project", back_populates="deliverables")
    
    @property
    def frequency_display(self) -> str:
        """Human-readable frequency name."""
        mapping = {
            "M": "Monthly",
            "Q": "Quarterly",
            "SA": "Semi-Annual",
            "A": "Annual",
            "OT": "One-Time"
        }
        return mapping.get(self.frequency, self.frequency)
    
    @property
    def is_overdue(self) -> bool:
        """Check if deliverable is past due date (uses UTC date for consistency)."""
        if self.status == DeliverableStatus.COMPLETED:
            return False
        return utc_today() > self.due_date

    @property
    def days_until_due(self) -> int:
        """Calculate days until due date (negative if overdue). Uses UTC date."""
        delta = self.due_date - utc_today()
        return delta.days
    
    def __repr__(self):
        return f"<Deliverable(id={self.id}, description='{self.description[:30]}...', due={self.due_date})>"
