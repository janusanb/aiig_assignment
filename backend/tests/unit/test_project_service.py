"""Unit tests for ProjectService (real DB with Excel data)."""
import pytest
from app.services import ProjectService


class TestProjectService:
    """ProjectService methods against seeded DB."""

    def test_get_all_returns_projects(self, db):
        service = ProjectService(db)
        projects = service.get_all()
        assert len(projects) >= 1
        for p in projects:
            assert p.id is not None
            assert p.name
            assert p.manager_id is not None
            assert p.manager is not None

    def test_get_by_id_existing(self, db):
        service = ProjectService(db)
        projects = service.get_all()
        assert len(projects) >= 1
        pid = projects[0].id
        project = service.get_by_id(pid)
        assert project is not None
        assert project.id == pid
        assert project.manager is not None

    def test_get_by_id_missing(self, db):
        service = ProjectService(db)
        project = service.get_by_id(999999)
        assert project is None

    def test_get_by_name_existing(self, db):
        service = ProjectService(db)
        projects = service.get_all()
        assert len(projects) >= 1
        name = projects[0].name
        project = service.get_by_name(name)
        assert project is not None
        assert project.name == name

    def test_get_by_name_missing(self, db):
        service = ProjectService(db)
        project = service.get_by_name("Nonexistent Project XYZ")
        assert project is None

    def test_search_partial_match(self, db):
        service = ProjectService(db)
        projects = service.get_all()
        assert len(projects) >= 1
        substring = projects[0].name[:5].lower()
        results = service.search(substring, limit=10)
        assert len(results) >= 1
        assert any(p.name.lower().find(substring) >= 0 for p in results)

    def test_search_case_insensitive(self, db):
        service = ProjectService(db)
        projects = service.get_all()
        assert len(projects) >= 1
        term = projects[0].name[:4].upper()
        results = service.search(term, limit=10)
        assert len(results) >= 1

    def test_search_respects_limit(self, db):
        service = ProjectService(db)
        results = service.search("project", limit=2)
        assert len(results) <= 2

    def test_get_with_stats_existing(self, db):
        service = ProjectService(db)
        projects = service.get_all()
        assert len(projects) >= 1
        pid = projects[0].id
        stats = service.get_with_stats(pid)
        assert stats is not None
        assert stats["id"] == pid
        assert "name" in stats
        assert "manager" in stats
        assert "total_deliverables" in stats
        assert "pending_deliverables" in stats
        assert "overdue_deliverables" in stats
        assert "upcoming_7_days" in stats

    def test_get_with_stats_missing(self, db):
        service = ProjectService(db)
        stats = service.get_with_stats(999999)
        assert stats is None

    def test_get_all_with_stats(self, db):
        service = ProjectService(db)
        results = service.get_all_with_stats()
        assert len(results) >= 1
        for r in results:
            assert "id" in r
            assert "total_deliverables" in r
            assert "manager" in r

    def test_get_search_results_shape(self, db):
        service = ProjectService(db)
        results = service.get_search_results("project", limit=5)
        assert isinstance(results, list)
        for r in results:
            assert "id" in r
            assert "name" in r
            assert "manager_name" in r
            assert "deliverable_count" in r
            assert isinstance(r["deliverable_count"], int)
