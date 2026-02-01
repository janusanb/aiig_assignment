"""Service layer for ProjectManager operations."""
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import ProjectManager, Project, Deliverable
from app.schemas import ProjectManagerCreate, ProjectManagerUpdate


class ProjectManagerService:
    """Service class for project manager operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[ProjectManager]:
        """Get all project managers."""
        return self.db.query(ProjectManager).order_by(ProjectManager.name).all()

    def get_by_id(self, manager_id: int) -> ProjectManager | None:
        """Get a project manager by ID."""
        return self.db.query(ProjectManager).filter(ProjectManager.id == manager_id).first()

    def get_by_name(self, name: str) -> ProjectManager | None:
        """Get a project manager by exact name match."""
        return self.db.query(ProjectManager).filter(ProjectManager.name == name).first()

    def get_or_create(self, name: str) -> tuple[ProjectManager, bool]:
        """
        Get existing manager or create new one.
        Returns tuple of (manager, created) where created is True if new.
        """
        manager = self.get_by_name(name)
        if manager:
            return manager, False

        manager = ProjectManager(name=name)
        self.db.add(manager)
        self.db.flush()
        return manager, True

    def create(self, data: ProjectManagerCreate) -> ProjectManager:
        """Create a new project manager."""
        manager = ProjectManager(**data.model_dump())
        self.db.add(manager)
        self.db.commit()
        self.db.refresh(manager)
        return manager

    def update(self, manager_id: int, data: ProjectManagerUpdate) -> ProjectManager | None:
        """Update an existing project manager."""
        manager = self.get_by_id(manager_id)
        if not manager:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(manager, field, value)

        self.db.commit()
        self.db.refresh(manager)
        return manager

    def delete(self, manager_id: int) -> bool:
        """Delete a project manager. Returns True if deleted."""
        manager = self.get_by_id(manager_id)
        if not manager:
            return False

        self.db.delete(manager)
        self.db.commit()
        return True

    def get_with_stats(self, manager_id: int) -> dict | None:
        """Get manager with project and deliverable counts."""
        manager = self.get_by_id(manager_id)
        if not manager:
            return None

        project_count = self.db.query(func.count(Project.id)).filter(
            Project.manager_id == manager_id
        ).scalar()

        deliverable_count = self.db.query(func.count(Deliverable.id)).join(
            Project
        ).filter(
            Project.manager_id == manager_id
        ).scalar()

        return {
            "id": manager.id,
            "name": manager.name,
            "email": manager.email,
            "created_at": manager.created_at,
            "updated_at": manager.updated_at,
            "project_count": project_count,
            "deliverable_count": deliverable_count
        }

    def get_all_with_stats(self) -> list[dict]:
        """Get all managers with their statistics."""
        managers = self.get_all()
        if not managers:
            return []

        manager_ids = [m.id for m in managers]
        project_counts = (
            self.db.query(Project.manager_id, func.count(Project.id).label("cnt"))
            .filter(Project.manager_id.in_(manager_ids))
            .group_by(Project.manager_id)
        ).all()
        project_count_by_id = {r.manager_id: r.cnt for r in project_counts}

        deliverable_counts = (
            self.db.query(Project.manager_id, func.count(Deliverable.id).label("cnt"))
            .join(Deliverable, Deliverable.project_id == Project.id)
            .filter(Project.manager_id.in_(manager_ids))
            .group_by(Project.manager_id)
        ).all()
        deliverable_count_by_id = {r.manager_id: r.cnt for r in deliverable_counts}

        return [
            {
                "id": m.id,
                "name": m.name,
                "email": m.email,
                "created_at": m.created_at,
                "updated_at": m.updated_at,
                "project_count": project_count_by_id.get(m.id, 0),
                "deliverable_count": deliverable_count_by_id.get(m.id, 0),
            }
            for m in managers
        ]
