"""Behavioral tests for Excel upload: POST /upload/preview and POST /upload/import."""
import io

import pandas as pd
import pytest
from fastapi.testclient import TestClient


PREFIX = "/api/v1"


def _csv_bytes(df: pd.DataFrame) -> bytes:
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    buf.seek(0)
    return buf.getvalue().encode("utf-8")


class TestUploadPreview:
    """POST /api/v1/upload/preview."""

    def test_preview_csv_200_and_schema(self, client: TestClient):
        """Preview valid CSV returns 200 and ExcelPreviewResult schema."""
        df = pd.DataFrame({
            "Project": ["PreviewProject"],
            "Deliverable": ["Preview deliverable"],
            "Due Date": ["2026-07-01"],
            "Frequency": ["Q"],
            "Project Manager": ["Preview Manager"],
        })
        content = _csv_bytes(df)
        r = client.post(
            f"{PREFIX}/upload/preview",
            files={"file": ("preview.csv", content, "text/csv")},
        )
        assert r.status_code == 200
        data = r.json()
        assert "filename" in data
        assert data["filename"] == "preview.csv"
        assert "total_rows" in data
        assert data["total_rows"] == 1
        assert "valid_rows" in data
        assert "invalid_rows" in data
        assert "preview_data" in data
        assert len(data["preview_data"]) == 1
        assert data["preview_data"][0]["is_valid"] is True
        assert "column_mapping" in data

    def test_preview_invalid_row_returns_validation_errors(self, client: TestClient):
        """Preview CSV with invalid row returns invalid_rows and validation_errors."""
        df = pd.DataFrame({
            "Project": [""],
            "Deliverable": ["D1"],
            "Due Date": ["2026-06-01"],
            "Frequency": ["OT"],
            "Project Manager": ["M1"],
        })
        content = _csv_bytes(df)
        r = client.post(
            f"{PREFIX}/upload/preview",
            files={"file": ("invalid.csv", content, "text/csv")},
        )
        assert r.status_code == 200
        data = r.json()
        assert data["invalid_rows"] >= 1
        assert len(data["preview_data"][0]["validation_errors"]) >= 1


class TestUploadImport:
    """POST /api/v1/upload/import."""

    def test_import_csv_200_and_counts(self, client: TestClient, restore_db_after):
        """Import valid CSV returns 200 and result with imported/skipped counts."""
        df = pd.DataFrame({
            "Project": ["BehavioralImportProject"],
            "Deliverable": ["Behavioral import deliverable"],
            "Due Date": ["2029-01-15"],
            "Frequency": ["A"],
            "Project Manager": ["BehavioralImportManager"],
        })
        content = _csv_bytes(df)
        r = client.post(
            f"{PREFIX}/upload/import",
            files={"file": ("import.csv", content, "text/csv")},
            params={"skip_invalid": True},
        )
        assert r.status_code == 200
        data = r.json()
        assert data["success"] is True
        assert data["filename"] == "import.csv"
        assert data["total_rows"] == 1
        assert data["imported_rows"] >= 1
        assert "projects_created" in data
        assert "managers_created" in data
        assert "deliverables_created" in data

    def test_import_bad_extension_400(self, client: TestClient):
        """Import with disallowed file type returns 400."""
        r = client.post(
            f"{PREFIX}/upload/import",
            files={"file": ("file.txt", b"not excel", "text/plain")},
        )
        assert r.status_code == 400
