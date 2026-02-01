"""Service layer for Project operations."""
from datetime import timedelta
from sqlalchemy.orm import Session, joinedload
from app.core.datetime_utils import utc_today
from sqlalchemy import case, func
from app.models import Project, ProjectManager, Deliverable, DeliverableStatus
from app.schemas import ProjectCreate, ProjectUpdate
from app.services.project_manager_service import ProjectManagerService


class ProjectService:
    """Service class for project operations."""

    def __init__(self, db: Session):
        self.db = db
        self.manager_service = ProjectManagerService(db)

    def get_all(self) -> list[Project]:
        """Get all projects with their managers."""
        return self.db.query(Project).options(
            joinedload(Project.manager)
        ).order_by(Project.name).all()

    def get_by_id(self, project_id: int) -> Project | None:
        """Get a project by ID with manager details."""
        return self.db.query(Project).options(
            joinedload(Project.manager)
        ).filter(Project.id == project_id).first()

    def get_by_name(self, name: str) -> Project | None:
        """Get a project by exact name match."""
        return self.db.query(Project).filter(Project.name == name).first()

    def search(self, query: str, limit: int = 10) -> list[Project]:
        """
        Search projects by name (case-insensitive partial match).
        Returns projects with manager info and deliverable count.
        """
        search_term = f"%{query}%"
        return self.db.query(Project).options(
            joinedload(Project.manager)
        ).filter(
            Project.name.ilike(search_term)
        ).order_by(Project.name).limit(limit).all()

    def get_or_create(self, name: str, manager_name: str) -> tuple[Project, bool]:
        """
        Get existing project or create new one with manager.
        Returns tuple of (project, created) where created is True if new.
        """
        project = self.get_by_name(name)
        if project:
            return project, False

        manager, _ = self.manager_service.get_or_create(manager_name)

        project = Project(name=name, manager_id=manager.id)
        self.db.add(project)
        self.db.flush()
        return project, True

    def create(self, data: ProjectCreate) -> Project:
        """Create a new project."""
        if data.manager_id:
            manager_id = data.manager_id
        elif data.manager_name:
            manager, _ = self.manager_service.get_or_create(data.manager_name)
            manager_id = manager.id
        else:
            raise ValueError("Either manager_id or manager_name must be provided")

        project = Project(
            name=data.name,
            description=data.description,
            manager_id=manager_id
        )
        self.db.add(project)
        self.db.commit()
        return self.get_by_id(project.id) or project

    def update(self, project_id: int, data: ProjectUpdate) -> Project | None:
        """Update an existing project."""
        project = self.get_by_id(project_id)
        if not project:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(project, field, value)

        self.db.commit()
        self.db.refresh(project)
        return project

    def delete(self, project_id: int) -> bool:
        """Delete a project and all its deliverables. Returns True if deleted."""
        project = self.get_by_id(project_id)
        if not project:
            return False

        self.db.delete(project)
        self.db.commit()
        return True

    def get_with_stats(self, project_id: int) -> dict | None:
        """Get project with deliverable statistics."""
        project = self.get_by_id(project_id)
        if not project:
            return None

        today = utc_today()
        week_from_now = today + timedelta(days=7)

        row = self.db.query(
            func.count(Deliverable.id).label("total"),
            func.count(case((Deliverable.status == DeliverableStatus.PENDING, 1))).label("pending"),
            func.count(
                case(
                    (
                        (Deliverable.status != DeliverableStatus.COMPLETED)
                        & (Deliverable.due_date < today),
                        1,
                    )
                )
            ).label("overdue"),
            func.count(
                case(
                    (
                        (Deliverable.status != DeliverableStatus.COMPLETED)
                        & (Deliverable.due_date >= today)
                        & (Deliverable.due_date <= week_from_now),
                        1,
                    )
                )
            ).label("upcoming_7_days"),
        ).filter(Deliverable.project_id == project_id).first()

        return {
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "manager_id": project.manager_id,
            "created_at": project.created_at,
            "updated_at": project.updated_at,
            "manager": project.manager,
            "total_deliverables": row.total or 0,
            "pending_deliverables": row.pending or 0,
            "overdue_deliverables": row.overdue or 0,
            "upcoming_7_days": row.upcoming_7_days or 0,
        }

    def get_all_with_stats(self) -> list[dict]:
        """Get all projects with their statistics."""
        projects = self.get_all()
        if not projects:
            return []

        today = utc_today()
        week_from_now = today + timedelta(days=7)
        project_ids = [p.id for p in projects]

        stats_rows = (
            self.db.query(
                Deliverable.project_id,
                func.count(Deliverable.id).label("total"),
                func.count(case((Deliverable.status == DeliverableStatus.PENDING, 1))).label("pending"),
                func.count(
                    case(
                        (
                            (Deliverable.status != DeliverableStatus.COMPLETED)
                            & (Deliverable.due_date < today),
                            1,
                        )
                    )
                ).label("overdue"),
                func.count(
                    case(
                        (
                            (Deliverable.status != DeliverableStatus.COMPLETED)
                            & (Deliverable.due_date >= today)
                            & (Deliverable.due_date <= week_from_now),
                            1,
                        )
                    )
                ).label("upcoming_7_days"),
            )
            .filter(Deliverable.project_id.in_(project_ids))
            .group_by(Deliverable.project_id)
        ).all()

        stats_by_id = {
            r.project_id: {
                "total_deliverables": r.total,
                "pending_deliverables": r.pending,
                "overdue_deliverables": r.overdue,
                "upcoming_7_days": r.upcoming_7_days,
            }
            for r in stats_rows
        }

        return [
            {
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "manager_id": p.manager_id,
                "created_at": p.created_at,
                "updated_at": p.updated_at,
                "manager": p.manager,
                "total_deliverables": stats_by_id.get(p.id, {}).get("total_deliverables", 0),
                "pending_deliverables": stats_by_id.get(p.id, {}).get("pending_deliverables", 0),
                "overdue_deliverables": stats_by_id.get(p.id, {}).get("overdue_deliverables", 0),
                "upcoming_7_days": stats_by_id.get(p.id, {}).get("upcoming_7_days", 0),
            }
            for p in projects
        ]

    def get_search_results(self, query: str, limit: int = 10) -> list[dict]:
        """Get search results with deliverable counts."""
        projects = self.search(query, limit)
        if not projects:
            return []

        project_ids = [p.id for p in projects]
        count_rows = (
            self.db.query(Deliverable.project_id, func.count(Deliverable.id).label("cnt"))
            .filter(Deliverable.project_id.in_(project_ids))
            .group_by(Deliverable.project_id)
        ).all()
        count_by_id = {r.project_id: r.cnt for r in count_rows}

        return [
            {
                "id": p.id,
                "name": p.name,
                "manager_name": p.manager.name,
                "deliverable_count": count_by_id.get(p.id, 0),
            }
            for p in projects
        ]
