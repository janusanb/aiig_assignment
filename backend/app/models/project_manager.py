"""ProjectManager model for storing project manager information."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base


class ProjectManager(Base):
    """
    Represents a project manager who oversees projects.
    
    Normalized to avoid duplicate storage of manager names
    and enable future features like manager dashboards.
    """
    __tablename__ = "project_managers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    projects = relationship("Project", back_populates="manager", lazy="dynamic")
    
    def __repr__(self):
        return f"<ProjectManager(id={self.id}, name='{self.name}')>"
