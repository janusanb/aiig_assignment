"""
Service for parsing, validating, and importing Excel files.
Handles the 'bonus bonus' feature of uploading Excel data.

Import flow: parse → validate → clean → load.
- Parse: read Excel/CSV, normalize column names (multiple header variations supported).
- Validate: required fields (project, deliverable, due_date, project_manager), optional frequency (M, Q, SA, A, OT); dates parseable; per-row error reporting.
- Clean: trim strings, collapse internal whitespace; coerce dates (including Excel serial numbers); normalize frequency.
- Load: insert managers → projects → deliverables in order; skip duplicates by (project, due_date, frequency, description).
"""
import io
from datetime import date, datetime
from pathlib import Path
from typing import Any, BinaryIO
import pandas as pd
from sqlalchemy.orm import Session

from app.models import ProjectManager, Project, Deliverable
from app.schemas.excel import (
    ExcelValidationError,
    ExcelUploadResult,
    ExcelPreviewRow,
    ExcelPreviewResult,
)
from app.services.project_manager_service import ProjectManagerService
from app.services.project_service import ProjectService


class ExcelParserService:
    """Service for parsing and importing Excel deliverable data."""

    COLUMN_MAPPINGS = {
        "project": ["Project", "project", "PROJECT", "Project Name", "project_name"],
        "deliverable": ["Deliverable", "deliverable", "DELIVERABLE", "Description", "description"],
        "due_date": ["Due Date", "due_date", "DUE DATE", "Due date", "DueDate", "Deadline"],
        "frequency": ["Frequency", "frequency", "FREQUENCY", "Freq"],
        "project_manager": ["Project Manager", "project_manager", "PROJECT MANAGER", "Manager", "PM"],
    }

    VALID_FREQUENCIES = {"M", "Q", "SA", "A", "OT"}

    FREQUENCY_ALIASES = {
        "M": "M",
        "MONTHLY": "M",
        "Q": "Q",
        "QUARTERLY": "Q",
        "SA": "SA",
        "SEMI-ANNUAL": "SA",
        "SEMIANNUAL": "SA",
        "A": "A",
        "ANNUAL": "A",
        "ANNUALLY": "A",
        "YEARLY": "A",
        "OT": "OT",
        "ONE-TIME": "OT",
        "ONETIME": "OT",
    }

    def __init__(self, db: Session):
        self.db = db
        self.manager_service = ProjectManagerService(db)
        self.project_service = ProjectService(db)

    def _find_column(self, df: pd.DataFrame, field: str) -> str | None:
        """Find the actual column name in DataFrame for a given field."""
        possible_names = self.COLUMN_MAPPINGS.get(field, [])
        for name in possible_names:
            if name in df.columns:
                return name
        return None

    def _normalize_columns(self, df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, str]]:
        """
        Normalize column names to standard format.
        Returns (normalized_df, column_mapping).
        """
        column_mapping = {}
        rename_map = {}

        for standard_name, possible_names in self.COLUMN_MAPPINGS.items():
            found_name = self._find_column(df, standard_name)
            if found_name:
                rename_map[found_name] = standard_name
                column_mapping[standard_name] = found_name

        df_normalized = df.rename(columns=rename_map)
        return df_normalized, column_mapping

    def _validate_row(self, row: pd.Series, row_num: int) -> tuple[bool, list[ExcelValidationError]]:
        """Validate a single row. Required: project, deliverable, due_date, project_manager. Frequency is optional (default OT)."""
        errors = []

        required_fields = ["project", "deliverable", "due_date", "project_manager"]
        for field in required_fields:
            value = row.get(field)
            if pd.isna(value) or (isinstance(value, str) and not value.strip()):
                errors.append(ExcelValidationError(
                    row=row_num,
                    column=field,
                    value=str(value) if not pd.isna(value) else None,
                    error=f"Required field '{field}' is empty"
                ))

        freq = row.get("frequency")
        if not pd.isna(freq):
            freq_str = str(freq).strip().upper()
            normalized_freq = self.FREQUENCY_ALIASES.get(freq_str, freq_str)
            if normalized_freq not in self.VALID_FREQUENCIES:
                errors.append(ExcelValidationError(
                    row=row_num,
                    column="frequency",
                    value=str(freq),
                    error=f"Invalid frequency '{freq}'. Must be one of: {self.VALID_FREQUENCIES}"
                ))

        due_date = row.get("due_date")
        if not pd.isna(due_date):
            if not isinstance(due_date, (date, datetime, pd.Timestamp)):
                try:
                    pd.to_datetime(due_date)
                except Exception:
                    errors.append(ExcelValidationError(
                        row=row_num,
                        column="due_date",
                        value=str(due_date),
                        error=f"Invalid date format: '{due_date}'"
                    ))

        return len(errors) == 0, errors

    def _clean_string(self, value: Any) -> str:
        """Clean and normalize string values: trim, collapse internal whitespace. Casing is preserved."""
        if pd.isna(value):
            return ""
        s = str(value).strip()
        return " ".join(s.split())

    def _parse_date(self, value: Any) -> date | None:
        """Parse date from various formats, including Excel date-as-number (serial days since 1899-12-30)."""
        if pd.isna(value):
            return None

        if isinstance(value, date) and not isinstance(value, datetime):
            return value

        if isinstance(value, datetime):
            return value.date()

        if isinstance(value, pd.Timestamp):
            return value.date()

        try:
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                parsed = pd.to_datetime(value, unit="D", origin="1899-12-30")
                return parsed.date()
            parsed = pd.to_datetime(value)
            return parsed.date()
        except Exception:
            return None

    def _parse_frequency(self, value: Any) -> str:
        """Normalize frequency value; unknown values default to OT for loading."""
        if pd.isna(value):
            return "OT"
        freq_str = str(value).strip().upper()
        return self.FREQUENCY_ALIASES.get(freq_str, freq_str if freq_str in self.VALID_FREQUENCIES else "OT")

    def preview(self, file: BinaryIO, filename: str) -> ExcelPreviewResult:
        """
        Preview Excel file contents without importing.
        Shows validation results for each row.
        """
        try:
            if filename.endswith('.csv'):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)
        except Exception:
            return ExcelPreviewResult(
                filename=filename,
                total_rows=0,
                valid_rows=0,
                invalid_rows=0,
                preview_data=[],
                column_mapping={}
            )

        df_normalized, column_mapping = self._normalize_columns(df)

        preview_rows = []
        valid_count = 0

        for idx, row in df_normalized.iterrows():
            row_num = idx + 2
            is_valid, errors = self._validate_row(row, row_num)

            if is_valid:
                valid_count += 1

            preview_row = ExcelPreviewRow(
                row_number=row_num,
                project=self._clean_string(row.get("project", "")),
                deliverable=self._clean_string(row.get("deliverable", "")),
                due_date=str(row.get("due_date", "")),
                frequency=self._clean_string(row.get("frequency", "")),
                project_manager=self._clean_string(row.get("project_manager", "")),
                is_valid=is_valid,
                validation_errors=[e.error for e in errors]
            )
            preview_rows.append(preview_row)

        return ExcelPreviewResult(
            filename=filename,
            total_rows=len(df_normalized),
            valid_rows=valid_count,
            invalid_rows=len(df_normalized) - valid_count,
            preview_data=preview_rows,
            column_mapping=column_mapping
        )

    def import_file(
        self,
        file: BinaryIO,
        filename: str,
        skip_invalid: bool = True
    ) -> ExcelUploadResult:
        """
        Import Excel file into database. Flow: parse → validate → clean → load.

        Args:
            file: File-like object containing Excel data
            filename: Original filename
            skip_invalid: If True, skip invalid rows; if False, fail on first error

        Returns:
            ExcelUploadResult with import statistics
        """
        try:
            if filename.endswith('.csv'):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)
        except Exception as e:
            return ExcelUploadResult(
                success=False,
                filename=filename,
                total_rows=0,
                imported_rows=0,
                skipped_rows=0,
                errors=[ExcelValidationError(
                    row=0,
                    column="file",
                    value=None,
                    error=f"Failed to read file: {str(e)}"
                )]
            )

        df_normalized, column_mapping = self._normalize_columns(df)

        missing_cols = []
        for field in ["project", "deliverable", "due_date", "project_manager"]:
            if field not in df_normalized.columns:
                missing_cols.append(field)

        if missing_cols:
            return ExcelUploadResult(
                success=False,
                filename=filename,
                total_rows=len(df),
                imported_rows=0,
                skipped_rows=len(df),
                errors=[ExcelValidationError(
                    row=0,
                    column="columns",
                    value=None,
                    error=f"Missing required columns: {missing_cols}"
                )]
            )

        all_errors = []
        imported_count = 0
        skipped_count = 0
        managers_created = 0
        projects_created = 0
        deliverables_created = 0

        manager_cache: dict[str, ProjectManager] = {}
        project_cache: dict[str, Project] = {}

        for idx, row in df_normalized.iterrows():
            row_num = idx + 2

            is_valid, errors = self._validate_row(row, row_num)

            if not is_valid:
                all_errors.extend(errors)
                if skip_invalid:
                    skipped_count += 1
                    continue
                else:
                    self.db.rollback()
                    return ExcelUploadResult(
                        success=False,
                        filename=filename,
                        total_rows=len(df),
                        imported_rows=0,
                        skipped_rows=idx,
                        errors=all_errors
                    )

            manager_name = self._clean_string(row["project_manager"])
            project_name = self._clean_string(row["project"])
            deliverable_desc = self._clean_string(row["deliverable"])
            due_date = self._parse_date(row["due_date"])
            frequency = self._parse_frequency(row.get("frequency", "OT"))

            try:
                if manager_name not in manager_cache:
                    manager, created = self.manager_service.get_or_create(manager_name)
                    manager_cache[manager_name] = manager
                    if created:
                        managers_created += 1
                manager = manager_cache[manager_name]

                if project_name not in project_cache:
                    project, created = self.project_service.get_or_create(
                        project_name,
                        manager_name
                    )
                    project_cache[project_name] = project
                    if created:
                        projects_created += 1
                project = project_cache[project_name]

                existing = self.db.query(Deliverable).filter(
                    Deliverable.project_id == project.id,
                    Deliverable.due_date == due_date,
                    Deliverable.frequency == frequency,
                    Deliverable.description == deliverable_desc,
                ).first()

                if existing:
                    skipped_count += 1
                    all_errors.append(ExcelValidationError(
                        row=row_num,
                        column="deliverable",
                        value=deliverable_desc,
                        error="Duplicate deliverable (same project, due date, frequency, and description)"
                    ))
                    continue

                deliverable = Deliverable(
                    project_id=project.id,
                    description=deliverable_desc,
                    due_date=due_date,
                    frequency=frequency
                )
                self.db.add(deliverable)
                self.db.flush()
                deliverables_created += 1
                imported_count += 1

            except Exception as e:
                all_errors.append(ExcelValidationError(
                    row=row_num,
                    column="processing",
                    value=None,
                    error=f"Error processing row: {str(e)}"
                ))
                skipped_count += 1
                continue

        try:
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            return ExcelUploadResult(
                success=False,
                filename=filename,
                total_rows=len(df),
                imported_rows=0,
                skipped_rows=len(df),
                errors=[ExcelValidationError(
                    row=0,
                    column="database",
                    value=None,
                    error=f"Database error: {str(e)}"
                )]
            )

        return ExcelUploadResult(
            success=True,
            filename=filename,
            total_rows=len(df),
            imported_rows=imported_count,
            skipped_rows=skipped_count,
            errors=all_errors,
            projects_created=projects_created,
            managers_created=managers_created,
            deliverables_created=deliverables_created
        )

    def import_from_path(self, file_path: str | Path) -> ExcelUploadResult:
        """Import Excel file from filesystem path."""
        path = Path(file_path)
        if not path.exists():
            return ExcelUploadResult(
                success=False,
                filename=str(path),
                total_rows=0,
                imported_rows=0,
                skipped_rows=0,
                errors=[ExcelValidationError(
                    row=0,
                    column="file",
                    value=str(path),
                    error="File not found"
                )]
            )

        with open(path, "rb") as f:
            return self.import_file(f, path.name)
