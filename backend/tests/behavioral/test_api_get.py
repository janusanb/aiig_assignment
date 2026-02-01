"""
Behavioral tests for GET REST endpoints.

Uses real app and real DB (seeded from Excel).
"""
import pytest
from fastapi.testclient import TestClient


PREFIX = "/api/v1"


class TestProjectsGet:
    """GET /api/v1/projects*."""

    def test_list_projects_200(self, client: TestClient):
        r = client.get(f"{PREFIX}/projects")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        if data:
            p = data[0]
            assert "id" in p
            assert "name" in p
            assert "manager" in p
            assert "total_deliverables" in p

    def test_search_projects_200(self, client: TestClient):
        r = client.get(f"{PREFIX}/projects/search", params={"q": "project", "limit": 5})
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        for p in data:
            assert "id" in p
            assert "name" in p
            assert "manager_name" in p
            assert "deliverable_count" in p

    def test_search_projects_empty_query_422(self, client: TestClient):
        r = client.get(f"{PREFIX}/projects/search", params={"q": ""})
        assert r.status_code == 422

    def test_get_project_by_id_200(self, client: TestClient):
        list_r = client.get(f"{PREFIX}/projects")
        assert list_r.status_code == 200
        data = list_r.json()
        if not data:
            pytest.skip("No projects in DB")
        pid = data[0]["id"]
        r = client.get(f"{PREFIX}/projects/{pid}")
        assert r.status_code == 200
        p = r.json()
        assert p["id"] == pid
        assert "name" in p
        assert "manager" in p
        assert "total_deliverables" in p

    def test_get_project_by_id_404(self, client: TestClient):
        r = client.get(f"{PREFIX}/projects/999999")
        assert r.status_code == 404

    def test_get_project_deliverables_200(self, client: TestClient):
        list_r = client.get(f"{PREFIX}/projects")
        assert list_r.status_code == 200
        data = list_r.json()
        if not data:
            pytest.skip("No projects in DB")
        pid = data[0]["id"]
        r = client.get(f"{PREFIX}/projects/{pid}/deliverables")
        assert r.status_code == 200
        items = r.json()
        assert isinstance(items, list)
        for d in items:
            assert "id" in d
            assert "project_id" in d
            assert "description" in d
            assert "due_date" in d
            assert "project_name" in d
            assert "manager_name" in d

    def test_get_project_deliverables_404(self, client: TestClient):
        r = client.get(f"{PREFIX}/projects/999999/deliverables")
        assert r.status_code == 404


class TestDeliverablesGet:
    """GET /api/v1/deliverables*."""

    def test_list_deliverables_200(self, client: TestClient):
        r = client.get(f"{PREFIX}/deliverables")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        if data:
            d = data[0]
            assert "id" in d
            assert "project_id" in d
            assert "description" in d
            assert "due_date" in d
            assert "project_name" in d
            assert "manager_name" in d

    def test_upcoming_200(self, client: TestClient):
        r = client.get(f"{PREFIX}/deliverables/upcoming", params={"days": 90})
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        for d in data:
            assert "due_date" in d
            assert "manager_name" in d

    def test_upcoming_filter_by_project_id_200(self, client: TestClient):
        list_r = client.get(f"{PREFIX}/projects")
        assert list_r.status_code == 200
        projects = list_r.json()
        if not projects:
            pytest.skip("No projects in DB")
        pid = projects[0]["id"]
        r = client.get(f"{PREFIX}/deliverables/upcoming", params={"days": 90, "project_id": pid})
        assert r.status_code == 200
        data = r.json()
        assert all(d["project_id"] == pid for d in data)

    def test_upcoming_include_overdue_returns_is_overdue_and_days_until_due(self, client: TestClient):
        """With include_overdue=true and project_id, response includes overdue items with correct flags."""
        from datetime import date

        from app.core.datetime_utils import utc_today

        list_r = client.get(f"{PREFIX}/projects")
        assert list_r.status_code == 200
        projects = list_r.json()
        if not projects:
            pytest.skip("No projects in DB")
        pid = projects[0]["id"]
        r = client.get(
            f"{PREFIX}/deliverables/upcoming",
            params={"days": 90, "project_id": pid, "include_overdue": True},
        )
        assert r.status_code == 200
        data = r.json()
        today = utc_today()
        for d in data:
            assert "is_overdue" in d
            assert "days_until_due" in d
            due = date.fromisoformat(d["due_date"]) if isinstance(d["due_date"], str) else d["due_date"]
            if due < today:
                assert d["is_overdue"] is True
                assert d["days_until_due"] < 0

    def test_overdue_200(self, client: TestClient):
        r = client.get(f"{PREFIX}/deliverables/overdue")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)

    def test_summary_200(self, client: TestClient):
        r = client.get(f"{PREFIX}/deliverables/summary")
        assert r.status_code == 200
        data = r.json()
        assert "total" in data
        assert "overdue" in data
        assert "due_today" in data
        assert "due_this_week" in data
        assert "due_this_month" in data

    def test_get_deliverable_by_id_200(self, client: TestClient):
        list_r = client.get(f"{PREFIX}/deliverables")
        assert list_r.status_code == 200
        data = list_r.json()
        if not data:
            pytest.skip("No deliverables in DB")
        did = data[0]["id"]
        r = client.get(f"{PREFIX}/deliverables/{did}")
        assert r.status_code == 200
        d = r.json()
        assert d["id"] == did
        assert "manager_name" in d
        assert "project_name" in d

    def test_get_deliverable_by_id_404(self, client: TestClient):
        r = client.get(f"{PREFIX}/deliverables/999999")
        assert r.status_code == 404


class TestManagersGet:
    """GET /api/v1/managers*."""

    def test_list_managers_200(self, client: TestClient):
        r = client.get(f"{PREFIX}/managers")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        if data:
            m = data[0]
            assert "id" in m
            assert "name" in m
            assert "project_count" in m
            assert "deliverable_count" in m

    def test_get_manager_by_id_200(self, client: TestClient):
        list_r = client.get(f"{PREFIX}/managers")
        assert list_r.status_code == 200
        data = list_r.json()
        if not data:
            pytest.skip("No managers in DB")
        mid = data[0]["id"]
        r = client.get(f"{PREFIX}/managers/{mid}")
        assert r.status_code == 200
        m = r.json()
        assert m["id"] == mid
        assert "name" in m
        assert "project_count" in m
        assert "deliverable_count" in m

    def test_get_manager_by_id_404(self, client: TestClient):
        r = client.get(f"{PREFIX}/managers/999999")
        assert r.status_code == 404
