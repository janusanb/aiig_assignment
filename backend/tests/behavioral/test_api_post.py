"""
Behavioral tests for POST endpoints (create) and duplicate handling.

Uses real app and real DB (seeded from Excel).
"""
import time
from datetime import timedelta

import pytest
from fastapi.testclient import TestClient

from app.core.datetime_utils import utc_today


PREFIX = "/api/v1"


class TestDeliverablesPost:
    """POST /api/v1/deliverables."""

    def test_create_deliverable_201(self, client: TestClient):
        """POST with valid body returns 201 and created deliverable."""
        list_r = client.get(f"{PREFIX}/projects")
        assert list_r.status_code == 200
        projects = list_r.json()
        if not projects:
            pytest.skip("No projects in DB")
        project_id = projects[0]["id"]
        due = (utc_today() + timedelta(days=9999)).isoformat()
        body = {
            "project_id": project_id,
            "description": f"Behavioral test deliverable 201 {time.time()}",
            "due_date": due,
            "frequency": "A",
        }
        r = client.post(f"{PREFIX}/deliverables", json=body)
        assert r.status_code == 201
        data = r.json()
        assert data["project_id"] == project_id
        assert data["description"] == body["description"]
        assert data["due_date"] == due
        assert data["frequency"] == "A"
        assert "id" in data
        assert "project_name" in data
        assert "manager_name" in data

    def test_create_deliverable_duplicate_409(self, client: TestClient):
        """POST same project_id, due_date, frequency, description twice returns 409 on second request."""
        list_r = client.get(f"{PREFIX}/projects")
        assert list_r.status_code == 200
        projects = list_r.json()
        if not projects:
            pytest.skip("No projects in DB")
        project_id = projects[0]["id"]
        due = (utc_today() + timedelta(days=8888)).isoformat()
        unique = time.time()
        body = {
            "project_id": project_id,
            "description": f"Duplicate test deliverable 409 {unique}",
            "due_date": due,
            "frequency": "Q",
        }
        first = client.post(f"{PREFIX}/deliverables", json=body)
        assert first.status_code == 201, first.json()
        second = client.post(f"{PREFIX}/deliverables", json=body)
        assert second.status_code == 409
        detail = second.json().get("detail", "")
        assert "already exists" in detail.lower() or "duplicate" in detail.lower()
