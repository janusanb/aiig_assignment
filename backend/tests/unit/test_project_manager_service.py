"""Unit tests for ProjectManagerService (real DB with Excel data)."""
import pytest
from app.services import ProjectManagerService


class TestProjectManagerService:
    """ProjectManagerService methods against seeded DB."""

    def test_get_all_returns_managers(self, db):
        service = ProjectManagerService(db)
        managers = service.get_all()
        assert len(managers) >= 1
        for m in managers:
            assert m.id is not None
            assert m.name

    def test_get_by_id_existing(self, db):
        service = ProjectManagerService(db)
        managers = service.get_all()
        assert len(managers) >= 1
        mid = managers[0].id
        manager = service.get_by_id(mid)
        assert manager is not None
        assert manager.id == mid

    def test_get_by_id_missing(self, db):
        service = ProjectManagerService(db)
        manager = service.get_by_id(999999)
        assert manager is None

    def test_get_by_name_existing(self, db):
        service = ProjectManagerService(db)
        managers = service.get_all()
        assert len(managers) >= 1
        name = managers[0].name
        manager = service.get_by_name(name)
        assert manager is not None
        assert manager.name == name

    def test_get_by_name_missing(self, db):
        service = ProjectManagerService(db)
        manager = service.get_by_name("Nonexistent Manager XYZ")
        assert manager is None

    def test_get_with_stats_existing(self, db):
        service = ProjectManagerService(db)
        managers = service.get_all()
        assert len(managers) >= 1
        mid = managers[0].id
        stats = service.get_with_stats(mid)
        assert stats is not None
        assert "id" in stats or hasattr(stats, "get")
        if isinstance(stats, dict):
            assert "project_count" in stats
            assert "deliverable_count" in stats
            assert isinstance(stats["project_count"], int)
            assert isinstance(stats["deliverable_count"], int)

    def test_get_with_stats_missing(self, db):
        service = ProjectManagerService(db)
        stats = service.get_with_stats(999999)
        assert stats is None

    def test_get_all_with_stats(self, db):
        service = ProjectManagerService(db)
        results = service.get_all_with_stats()
        assert len(results) >= 1
        for r in results:
            assert isinstance(r, dict)
            assert "project_count" in r
            assert "deliverable_count" in r
