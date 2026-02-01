"""API routes for Excel file upload and import. Import flow: parse → validate → clean → load."""
import io
from pathlib import Path
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.schemas import ExcelUploadResult, ExcelPreviewResult
from app.services import ExcelParserService

router = APIRouter(prefix="/upload", tags=["File Upload"])
settings = get_settings()


def validate_file(file: UploadFile) -> None:
    """Validate uploaded file."""
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided"
        )

    ext = Path(file.filename).suffix.lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type '{ext}' not allowed. Allowed types: {settings.ALLOWED_EXTENSIONS}"
        )


@router.post("/preview", response_model=ExcelPreviewResult)
async def preview_excel(
    file: UploadFile = File(..., description="Excel file to preview"),
    db: Session = Depends(get_db)
):
    """
    Preview Excel file without importing. Uses same parse → validate → clean pipeline;
    returns validation results per row (valid/invalid and errors). No database changes.
    """
    validate_file(file)

    service = ExcelParserService(db)

    content = await file.read()
    file_obj = io.BytesIO(content)

    return service.preview(file_obj, file.filename)


@router.post("/import", response_model=ExcelUploadResult)
async def import_excel(
    file: UploadFile = File(..., description="Excel file to import"),
    skip_invalid: bool = True,
    db: Session = Depends(get_db)
):
    validate_file(file)

    service = ExcelParserService(db)

    content = await file.read()

    if settings.UPLOAD_DIR:
        import uuid
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = uuid.uuid4().hex[:8]
        safe_filename = f"{timestamp}_{unique_id}_{file.filename}"
        save_path = settings.UPLOAD_DIR / safe_filename

        with open(save_path, "wb") as f:
            f.write(content)

    file_obj = io.BytesIO(content)

    result = service.import_file(file_obj, file.filename, skip_invalid=skip_invalid)

    if not result.success and not skip_invalid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Import failed due to validation errors",
                "errors": [e.model_dump() for e in result.errors]
            }
        )

    return result


@router.get("/template")
async def get_template():
    """
    Expected Excel template: column names, valid values, and deduplication rule.
    Duplicates are determined by (project, due_date, frequency, description).
    """
    return {
        "columns": {
            "Project": {
                "description": "Name of the infrastructure project",
                "type": "string",
                "required": True,
                "example": "New Toronto Hospital"
            },
            "Deliverable": {
                "description": "Description of the deliverable",
                "type": "string",
                "required": True,
                "example": "Submit monthly progress report"
            },
            "Due Date": {
                "description": "Due date for the deliverable",
                "type": "date",
                "required": True,
                "format": "YYYY-MM-DD or Excel date",
                "example": "2026-02-28"
            },
            "Frequency": {
                "description": "How often this deliverable recurs",
                "type": "string",
                "required": False,
                "valid_values": {
                    "M": "Monthly",
                    "Q": "Quarterly",
                    "SA": "Semi-Annual",
                    "A": "Annual",
                    "OT": "One-Time"
                },
                "default": "OT",
                "example": "M"
            },
            "Project Manager": {
                "description": "Name of the project manager",
                "type": "string",
                "required": True,
                "example": "Jane Doe"
            }
        },
        "notes": [
            "Column names are case-insensitive",
            "Extra columns will be ignored",
            "Duplicate deliverables (same project, due date, frequency, and description) will be skipped",
            "New projects and managers will be created automatically"
        ]
    }
