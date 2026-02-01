"""Pydantic schemas for Excel file upload and parsing."""
from datetime import date
from pydantic import BaseModel, ConfigDict, Field


class ExcelRowData(BaseModel):
    """Schema representing a single row from the Excel file."""
    model_config = ConfigDict(populate_by_name=True)

    project: str = Field(..., alias="Project")
    deliverable: str = Field(..., alias="Deliverable")
    due_date: date = Field(..., alias="Due Date")
    frequency: str = Field(..., alias="Frequency")
    project_manager: str = Field(..., alias="Project Manager")


class ExcelValidationError(BaseModel):
    """Schema for validation errors during Excel parsing."""
    row: int
    column: str
    value: str | None
    error: str


class ExcelUploadResult(BaseModel):
    """Schema for Excel upload results."""
    success: bool
    filename: str
    total_rows: int
    imported_rows: int
    skipped_rows: int
    errors: list[ExcelValidationError] = []
    projects_created: int = 0
    managers_created: int = 0
    deliverables_created: int = 0


class ExcelPreviewRow(BaseModel):
    """Schema for previewing Excel data before import."""
    row_number: int
    project: str
    deliverable: str
    due_date: str
    frequency: str
    project_manager: str
    is_valid: bool
    validation_errors: list[str] = []


class ExcelPreviewResult(BaseModel):
    """Schema for Excel preview results."""
    filename: str
    total_rows: int
    valid_rows: int
    invalid_rows: int
    preview_data: list[ExcelPreviewRow]
    column_mapping: dict[str, str]
