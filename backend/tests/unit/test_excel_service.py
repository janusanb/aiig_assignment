"""Unit tests for ExcelParserService: validation, cleaning, column normalization, duplicate handling."""
import io

import pandas as pd
import pytest

from app.services import ExcelParserService


def _csv_bytes(df: pd.DataFrame) -> bytes:
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    buf.seek(0)
    return buf.getvalue().encode("utf-8")


def _to_file_like(content: bytes) -> io.BytesIO:
    return io.BytesIO(content)


class TestExcelServiceColumnNormalization:
    """Column name normalization and missing columns."""

    def test_normalize_columns_maps_alternate_names(self, db):
        """Alternate column names (e.g. Project Name, PM) are normalized."""
        df = pd.DataFrame({
            "Project Name": ["P1"],
            "Deliverable": ["D1"],
            "Due Date": ["2026-06-01"],
            "Frequency": ["M"],
            "PM": ["Manager One"],
        })
        content = _csv_bytes(df)
        service = ExcelParserService(db)
        result = service.preview(_to_file_like(content), "test.csv")
        assert result.total_rows == 1
        assert result.column_mapping
        assert result.preview_data[0].project == "P1"
        assert result.preview_data[0].project_manager == "Manager One"

    def test_missing_required_columns_returns_error(self, db):
        """Missing required columns (e.g. due_date, project_manager) returns error on import."""
        df = pd.DataFrame({
            "Project": ["P1"],
            "Deliverable": ["D1"],
        })
        content = _csv_bytes(df)
        service = ExcelParserService(db)
        result = service.import_file(_to_file_like(content), "test.csv")
        assert result.success is False
        assert result.imported_rows == 0
        assert any("Missing" in e.error or "columns" in e.error for e in result.errors)


class TestExcelServiceValidation:
    """Required fields, frequency, date validation."""

    def test_required_field_empty_invalid(self, db):
        """Row with empty required field (e.g. project) is invalid in preview."""
        df = pd.DataFrame({
            "Project": [""],
            "Deliverable": ["D1"],
            "Due Date": ["2026-06-01"],
            "Frequency": ["OT"],
            "Project Manager": ["M1"],
        })
        content = _csv_bytes(df)
        service = ExcelParserService(db)
        result = service.preview(_to_file_like(content), "test.csv")
        assert result.invalid_rows >= 1
        row0 = result.preview_data[0]
        assert row0.is_valid is False
        assert any("project" in e.lower() or "empty" in e.lower() for e in row0.validation_errors)

    def test_invalid_frequency_invalid(self, db):
        """Row with invalid frequency (e.g. X) is invalid."""
        df = pd.DataFrame({
            "Project": ["P1"],
            "Deliverable": ["D1"],
            "Due Date": ["2026-06-01"],
            "Frequency": ["X"],
            "Project Manager": ["M1"],
        })
        content = _csv_bytes(df)
        service = ExcelParserService(db)
        result = service.preview(_to_file_like(content), "test.csv")
        assert result.invalid_rows >= 1
        assert any("frequency" in e.lower() or "invalid" in e.lower() for e in result.preview_data[0].validation_errors)

    def test_invalid_date_string_invalid(self, db):
        """Row with unparseable date string is invalid."""
        df = pd.DataFrame({
            "Project": ["P1"],
            "Deliverable": ["D1"],
            "Due Date": ["notadate"],
            "Frequency": ["OT"],
            "Project Manager": ["M1"],
        })
        content = _csv_bytes(df)
        service = ExcelParserService(db)
        result = service.preview(_to_file_like(content), "test.csv")
        assert result.invalid_rows >= 1

    def test_excel_serial_date_parsed(self, db, restore_db_after):
        """Excel serial date (integer) is parsed correctly."""
        df = pd.DataFrame({
            "Project": ["SerialDateProject"],
            "Deliverable": ["D1"],
            "Due Date": [44927],
            "Frequency": ["OT"],
            "Project Manager": ["SerialDateManager"],
        })
        content = _csv_bytes(df)
        service = ExcelParserService(db)
        result = service.preview(_to_file_like(content), "test.csv")
        assert result.valid_rows >= 1
        service2 = ExcelParserService(db)
        import_result = service2.import_file(_to_file_like(content), "test.csv")
        assert import_result.success
        assert import_result.imported_rows >= 1


class TestExcelServiceCleaning:
    """String trim, whitespace collapse, frequency normalization."""

    def test_clean_string_trim_and_collapse_spaces(self, db):
        """Strings are trimmed and internal multiple spaces collapsed."""
        df = pd.DataFrame({
            "Project": ["  Proj   Name  "],
            "Deliverable": ["  Deliverable   here  "],
            "Due Date": ["2026-06-01"],
            "Frequency": [" M "],
            "Project Manager": [" Manager  One "],
        })
        content = _csv_bytes(df)
        service = ExcelParserService(db)
        result = service.preview(_to_file_like(content), "test.csv")
        assert result.valid_rows >= 1
        row0 = result.preview_data[0]
        assert row0.project == "Proj Name"
        assert row0.deliverable == "Deliverable here"
        assert row0.project_manager == "Manager One"
        assert row0.frequency == "M"

    def test_frequency_normalized_to_code(self, db, restore_db_after):
        """Frequency 'Quarterly' is normalized to 'Q' on import."""
        df = pd.DataFrame({
            "Project": ["FreqNormProject"],
            "Deliverable": ["D1"],
            "Due Date": ["2027-01-01"],
            "Frequency": ["Quarterly"],
            "Project Manager": ["FreqNormManager"],
        })
        content = _csv_bytes(df)
        service = ExcelParserService(db)
        result = service.import_file(_to_file_like(content), "test.csv")
        assert result.success
        assert result.imported_rows >= 1


class TestExcelServiceDuplicateHandling:
    """Duplicate rows (same project, due_date, frequency, description) are skipped."""

    def test_duplicate_row_skipped(self, db, restore_db_after):
        """Second row with same (project, due_date, frequency, description) is skipped."""
        df = pd.DataFrame({
            "Project": ["DupTestProject"],
            "Deliverable": ["Same deliverable"],
            "Due Date": ["2028-06-15"],
            "Frequency": ["A"],
            "Project Manager": ["DupTestManager"],
        })
        df = pd.concat([df, df], ignore_index=True)
        content = _csv_bytes(df)
        service = ExcelParserService(db)
        result = service.import_file(_to_file_like(content), "test.csv")
        assert result.success
        assert result.imported_rows == 1
        assert result.skipped_rows == 1
        assert any("Duplicate" in e.error for e in result.errors)
