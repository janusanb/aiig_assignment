"""Unit tests for DeliverableService (real DB with Excel data)."""
import time
from datetime import timedelta

import pytest

from app.core.datetime_utils import utc_today
from app.models import Deliverable, DeliverableStatus
from app.schemas import DeliverableCreate
from app.services import DeliverableService
from app.services.deliverable_service import DuplicateDeliverableError


class TestDeliverableService:
    """DeliverableService methods against seeded DB."""

    def test_get_all_returns_deliverables(self, db):
        service = DeliverableService(db)
        deliverables = service.get_all(include_completed=False)
        assert isinstance(deliverables, list)
        for d in deliverables:
            assert d.id is not None
            assert d.project_id is not None
            assert d.description
            assert d.due_date is not None
            assert d.project is not None
            assert d.project.manager is not None

    def test_get_by_id_existing(self, db):
        service = DeliverableService(db)
        all_d = service.get_all(include_completed=False)
        if not all_d:
            pytest.skip("No deliverables in DB")
        did = all_d[0].id
        d = service.get_by_id(did)
        assert d is not None
        assert d.id == did
        assert d.project is not None
        assert d.project.manager is not None

    def test_get_by_id_missing(self, db):
        service = DeliverableService(db)
        d = service.get_by_id(999999)
        assert d is None

    def test_get_by_project(self, db):
        service = DeliverableService(db)
        all_d = service.get_all(include_completed=False)
        if not all_d:
            pytest.skip("No deliverables in DB")
        project_id = all_d[0].project_id
        by_project = service.get_by_project(project_id)
        assert isinstance(by_project, list)
        assert all(d.project_id == project_id for d in by_project)
        dates = [d.due_date for d in by_project]
        assert dates == sorted(dates)

    def test_get_by_project_respects_limit(self, db):
        service = DeliverableService(db)
        all_d = service.get_all(include_completed=False)
        if not all_d:
            pytest.skip("No deliverables in DB")
        project_id = all_d[0].project_id
        limited = service.get_by_project(project_id, limit=2)
        assert len(limited) <= 2

    def test_get_upcoming_returns_list(self, db):
        service = DeliverableService(db)
        results = service.get_upcoming(days=365)
        assert isinstance(results, list)
        for d in results:
            assert d.due_date is not None
            assert d.project is not None
            assert d.project.manager is not None

    def test_get_upcoming_filter_by_project_id(self, db):
        service = DeliverableService(db)
        all_d = service.get_all(include_completed=False)
        if not all_d:
            pytest.skip("No deliverables in DB")
        project_id = all_d[0].project_id
        results = service.get_upcoming(days=365, project_id=project_id)
        assert all(d.project_id == project_id for d in results)

    def test_get_upcoming_sorted_by_due_date(self, db):
        service = DeliverableService(db)
        results = service.get_upcoming(days=365)
        if len(results) < 2:
            pytest.skip("Need at least 2 upcoming for sort check")
        dates = [d.due_date for d in results]
        assert dates == sorted(dates)

    def test_get_overdue_returns_list(self, db):
        service = DeliverableService(db)
        results = service.get_overdue()
        assert isinstance(results, list)

    def test_get_summary_shape(self, db):
        service = DeliverableService(db)
        summary = service.get_summary()
        assert "total" in summary
        assert "overdue" in summary
        assert "due_today" in summary
        assert "due_this_week" in summary
        assert "due_this_month" in summary
        assert all(isinstance(summary[k], int) for k in summary)

    def test_get_summary_filter_by_project_id(self, db):
        service = DeliverableService(db)
        all_d = service.get_all(include_completed=False)
        if not all_d:
            pytest.skip("No deliverables in DB")
        project_id = all_d[0].project_id
        summary = service.get_summary(project_id=project_id)
        assert "total" in summary

    def test_to_response_dict_shape(self, db):
        service = DeliverableService(db)
        all_d = service.get_all(include_completed=False)
        if not all_d:
            pytest.skip("No deliverables in DB")
        d = all_d[0]
        out = service.to_response_dict(d)
        assert "id" in out
        assert "project_id" in out
        assert "description" in out
        assert "due_date" in out
        assert "project_name" in out
        assert "manager_name" in out
        assert "frequency_display" in out
        assert "days_until_due" in out
        assert "is_overdue" in out

    def test_overdue_deliverable_has_is_overdue_true_and_negative_days_until_due(self, db, restore_db_after):
        """A deliverable with due_date yesterday has is_overdue=True and days_until_due=-1."""
        service = DeliverableService(db)
        all_d = service.get_all(include_completed=False)
        if not all_d:
            pytest.skip("No deliverables in DB")
        project_id = all_d[0].project_id
        yesterday = utc_today() - timedelta(days=1)
        overdue = Deliverable(
            project_id=project_id,
            description="Test overdue deliverable",
            due_date=yesterday,
            frequency="OT",
            status=DeliverableStatus.PENDING,
        )
        db.add(overdue)
        db.commit()
        loaded = service.get_by_id(overdue.id)
        assert loaded is not None
        out = service.to_response_dict(loaded)
        assert out["is_overdue"] is True
        assert out["days_until_due"] == -1

    def test_get_upcoming_with_include_overdue_returns_overdue_with_correct_flags(self, db, restore_db_after):
        """get_upcoming(include_overdue=True, project_id=X) returns overdue items with is_overdue True."""
        service = DeliverableService(db)
        all_d = service.get_all(include_completed=False)
        if not all_d:
            pytest.skip("No deliverables in DB")
        project_id = all_d[0].project_id
        yesterday = utc_today() - timedelta(days=1)
        overdue = Deliverable(
            project_id=project_id,
            description="Upcoming test overdue",
            due_date=yesterday,
            frequency="OT",
            status=DeliverableStatus.PENDING,
        )
        db.add(overdue)
        db.commit()
        results = service.get_upcoming(
            days=30, project_id=project_id, include_overdue=True
        )
        results_dict = [service.to_response_dict(d) for d in results]
        overdue_items = [r for r in results_dict if r["due_date"] == yesterday]
        assert len(overdue_items) >= 1
        for r in overdue_items:
            assert r["is_overdue"] is True
            assert r["days_until_due"] <= -1

    def test_create_duplicate_raises_duplicate_deliverable_error(self, db, restore_db_after):
        """Creating a second deliverable with same project_id, due_date, frequency, description raises DuplicateDeliverableError."""
        service = DeliverableService(db)
        all_d = service.get_all(include_completed=False)
        if not all_d:
            pytest.skip("No deliverables in DB")
        project_id = all_d[0].project_id
        due = utc_today() + timedelta(days=7777)
        data = DeliverableCreate(
            project_id=project_id,
            description=f"Unit test duplicate deliverable {time.time()}",
            due_date=due,
            frequency="Q",
        )
        first = service.create(data)
        assert first.id is not None
        with pytest.raises(DuplicateDeliverableError) as exc_info:
            service.create(data)
        assert "already exists" in str(exc_info.value).lower()
