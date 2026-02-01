"""Service layer for Deliverable operations."""
from datetime import timedelta
from sqlalchemy import case, func


class DuplicateDeliverableError(ValueError):
    """Raised when a deliverable duplicate (same project, due_date, frequency, description) already exists."""

from app.core.datetime_utils import utc_today
from sqlalchemy.orm import Session, joinedload
from app.models import Deliverable, Project, ProjectManager, DeliverableStatus
from app.schemas import DeliverableCreate, DeliverableUpdate, DeliverableFilter
from app.services.project_service import ProjectService


class DeliverableService:
    """Service class for deliverable operations."""

    def __init__(self, db: Session):
        self.db = db
        self.project_service = ProjectService(db)

    def get_all(self, include_completed: bool = False) -> list[Deliverable]:
        """Get all deliverables with project info."""
        query = self.db.query(Deliverable).options(
            joinedload(Deliverable.project).joinedload(Project.manager)
        )

        if not include_completed:
            query = query.filter(Deliverable.status != DeliverableStatus.COMPLETED)

        return query.order_by(Deliverable.due_date).all()

    def get_by_id(self, deliverable_id: int) -> Deliverable | None:
        """Get a deliverable by ID with project details."""
        return self.db.query(Deliverable).options(
            joinedload(Deliverable.project).joinedload(Project.manager)
        ).filter(Deliverable.id == deliverable_id).first()

    def get_by_project(
        self,
        project_id: int,
        include_completed: bool = False,
        limit: int | None = None
    ) -> list[Deliverable]:
        """Get all deliverables for a specific project."""
        query = self.db.query(Deliverable).options(
            joinedload(Deliverable.project).joinedload(Project.manager)
        ).filter(Deliverable.project_id == project_id)

        if not include_completed:
            query = query.filter(Deliverable.status != DeliverableStatus.COMPLETED)

        query = query.order_by(Deliverable.due_date)

        if limit:
            query = query.limit(limit)

        return query.all()

    def get_upcoming(
        self,
        days: int = 30,
        project_id: int | None = None,
        manager_id: int | None = None,
        include_overdue: bool = False,
    ) -> list[Deliverable]:
        """Get deliverables due within the specified number of days.

        When include_overdue is True and project_id is set, also includes overdue
        deliverables for that project (due_date < today) for visibility and proactive monitoring.
        """
        today = utc_today()
        end_date = today + timedelta(days=days)

        if include_overdue and project_id is not None:
            date_filter = Deliverable.due_date <= end_date
        else:
            date_filter = (Deliverable.due_date >= today) & (Deliverable.due_date <= end_date)

        query = self.db.query(Deliverable).options(
            joinedload(Deliverable.project).joinedload(Project.manager)
        ).filter(
            Deliverable.status != DeliverableStatus.COMPLETED,
            date_filter
        )

        if project_id:
            query = query.filter(Deliverable.project_id == project_id)

        if manager_id:
            query = query.join(Project).filter(Project.manager_id == manager_id)

        return query.order_by(Deliverable.due_date).all()

    def get_overdue(
        self,
        project_id: int | None = None,
        manager_id: int | None = None
    ) -> list[Deliverable]:
        """Get all overdue deliverables."""
        today = utc_today()

        query = self.db.query(Deliverable).options(
            joinedload(Deliverable.project).joinedload(Project.manager)
        ).filter(
            Deliverable.status != DeliverableStatus.COMPLETED,
            Deliverable.due_date < today
        )

        if project_id:
            query = query.filter(Deliverable.project_id == project_id)

        if manager_id:
            query = query.join(Project).filter(Project.manager_id == manager_id)

        return query.order_by(Deliverable.due_date).all()

    def filter(self, filters: DeliverableFilter) -> list[Deliverable]:
        """Filter deliverables based on multiple criteria."""
        query = self.db.query(Deliverable).options(
            joinedload(Deliverable.project).joinedload(Project.manager)
        )

        if filters.project_id:
            query = query.filter(Deliverable.project_id == filters.project_id)

        if filters.project_name:
            query = query.join(Project).filter(
                Project.name.ilike(f"%{filters.project_name}%")
            )

        if filters.manager_id:
            query = query.join(Project).filter(Project.manager_id == filters.manager_id)

        if filters.status:
            query = query.filter(Deliverable.status == filters.status)

        if filters.frequency:
            query = query.filter(Deliverable.frequency == filters.frequency)

        if filters.due_before:
            query = query.filter(Deliverable.due_date <= filters.due_before)

        if filters.due_after:
            query = query.filter(Deliverable.due_date >= filters.due_after)

        if not filters.include_completed:
            query = query.filter(Deliverable.status != DeliverableStatus.COMPLETED)

        if filters.search:
            query = query.filter(
                Deliverable.description.ilike(f"%{filters.search}%")
            )

        return query.order_by(Deliverable.due_date).all()

    def find_duplicate(
        self,
        project_id: int,
        due_date,
        frequency: str,
        description: str,
    ) -> Deliverable | None:
        """Return an existing deliverable with same project_id, due_date, frequency, and description, or None."""
        return self.db.query(Deliverable).filter(
            Deliverable.project_id == project_id,
            Deliverable.due_date == due_date,
            Deliverable.frequency == frequency,
            Deliverable.description == description,
        ).first()

    def create(self, data: DeliverableCreate) -> Deliverable:
        """Create a new deliverable."""
        if data.project_id:
            project_id = data.project_id
        elif data.project_name:
            project = self.project_service.get_by_name(data.project_name)
            if not project:
                raise ValueError(f"Project '{data.project_name}' not found")
            project_id = project.id
        else:
            raise ValueError("Either project_id or project_name must be provided")

        duplicate = self.find_duplicate(
            project_id=project_id,
            due_date=data.due_date,
            frequency=data.frequency,
            description=data.description,
        )
        if duplicate:
            raise DuplicateDeliverableError(
                "A deliverable for this project with the same due date, frequency, and description already exists"
            )

        deliverable = Deliverable(
            project_id=project_id,
            description=data.description,
            due_date=data.due_date,
            frequency=data.frequency,
            notes=data.notes
        )
        self.db.add(deliverable)
        self.db.commit()
        return self.get_by_id(deliverable.id) or deliverable

    def create_bulk(self, deliverables_data: list[dict]) -> list[Deliverable]:
        """Create multiple deliverables efficiently."""
        deliverables = []
        for data in deliverables_data:
            deliverable = Deliverable(**data)
            self.db.add(deliverable)
            deliverables.append(deliverable)

        self.db.flush()
        return deliverables

    def update(self, deliverable_id: int, data: DeliverableUpdate) -> Deliverable | None:
        """Update an existing deliverable."""
        deliverable = self.get_by_id(deliverable_id)
        if not deliverable:
            return None

        update_data = data.model_dump(exclude_unset=True)

        if update_data.get("status") == DeliverableStatus.COMPLETED:
            from datetime import datetime
            update_data["completed_at"] = datetime.utcnow()

        for field, value in update_data.items():
            setattr(deliverable, field, value)

        self.db.commit()
        self.db.refresh(deliverable)
        return deliverable

    def mark_complete(self, deliverable_id: int) -> Deliverable | None:
        """Mark a deliverable as completed."""
        return self.update(
            deliverable_id,
            DeliverableUpdate(status=DeliverableStatus.COMPLETED)
        )

    def delete(self, deliverable_id: int) -> bool:
        """Delete a deliverable. Returns True if deleted."""
        deliverable = self.get_by_id(deliverable_id)
        if not deliverable:
            return False

        self.db.delete(deliverable)
        self.db.commit()
        return True

    def get_summary(
        self,
        project_id: int | None = None,
        manager_id: int | None = None
    ) -> dict:
        """Get summary statistics for deliverables."""
        today = utc_today()
        week_from_now = today + timedelta(days=7)
        month_from_now = today + timedelta(days=30)

        query = self.db.query(
            func.count(Deliverable.id).label("total"),
            func.count(case((Deliverable.due_date < today, 1))).label("overdue"),
            func.count(case((Deliverable.due_date == today, 1))).label("due_today"),
            func.count(
                case(
                    (
                        (Deliverable.due_date >= today)
                        & (Deliverable.due_date <= week_from_now),
                        1,
                    )
                )
            ).label("due_this_week"),
            func.count(
                case(
                    (
                        (Deliverable.due_date >= today)
                        & (Deliverable.due_date <= month_from_now),
                        1,
                    )
                )
            ).label("due_this_month"),
        ).filter(Deliverable.status != DeliverableStatus.COMPLETED)

        if project_id:
            query = query.filter(Deliverable.project_id == project_id)

        if manager_id:
            query = query.join(Project).filter(Project.manager_id == manager_id)

        row = query.first()
        return {
            "total": row.total or 0,
            "overdue": row.overdue or 0,
            "due_today": row.due_today or 0,
            "due_this_week": row.due_this_week or 0,
            "due_this_month": row.due_this_month or 0,
        }

    def to_response_dict(self, deliverable: Deliverable) -> dict:
        """Convert deliverable to response dict with computed fields."""
        return {
            "id": deliverable.id,
            "project_id": deliverable.project_id,
            "description": deliverable.description,
            "due_date": deliverable.due_date,
            "frequency": deliverable.frequency,
            "status": deliverable.status,
            "notes": deliverable.notes,
            "completed_at": deliverable.completed_at,
            "created_at": deliverable.created_at,
            "updated_at": deliverable.updated_at,
            "project_name": deliverable.project.name,
            "manager_name": deliverable.project.manager.name,
            "frequency_display": deliverable.frequency_display,
            "days_until_due": deliverable.days_until_due,
            "is_overdue": deliverable.is_overdue
        }
