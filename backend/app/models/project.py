"""Project model for storing infrastructure project information."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Project(Base):
    """
    Represents an infrastructure project managed by AIIG.
    
    Each project has a manager and multiple deliverables.
    """
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(String(1000), nullable=True)
    manager_id = Column(Integer, ForeignKey("project_managers.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    manager = relationship("ProjectManager", back_populates="projects")
    deliverables = relationship(
        "Deliverable", 
        back_populates="project", 
        lazy="dynamic",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}')>"
