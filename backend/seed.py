#!/usr/bin/env python3
"""
Database seeding script.

Initializes the database and loads the initial dataset from Excel.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import init_db, SessionLocal
from app.services import ExcelParserService


def seed_database(excel_path: str | None = None):
    """
    Initialize database and seed with data from Excel file.

    Args:
        excel_path: Path to Excel file. Defaults to data/FSD_deliverable_dataset.xlsx
    """
    print("Initializing database tables...")
    init_db()
    print("✓ Database tables created")

    if excel_path is None:
        excel_path = Path(__file__).parent / "data" / "FSD_deliverable_dataset.xlsx"
    else:
        excel_path = Path(excel_path)

    if not excel_path.exists():
        print(f"✗ Excel file not found: {excel_path}")
        return False

    print(f"Importing data from {excel_path}...")

    db = SessionLocal()
    try:
        service = ExcelParserService(db)
        result = service.import_from_path(excel_path)

        if result.success:
            print(f"✓ Import successful!")
            print(f"  - Total rows: {result.total_rows}")
            print(f"  - Imported: {result.imported_rows}")
            print(f"  - Skipped: {result.skipped_rows}")
            print(f"  - Managers created: {result.managers_created}")
            print(f"  - Projects created: {result.projects_created}")
            print(f"  - Deliverables created: {result.deliverables_created}")

            if result.errors:
                print(f"  - Warnings: {len(result.errors)}")
                for error in result.errors[:5]:
                    print(f"    Row {error.row}: {error.error}")
                if len(result.errors) > 5:
                    print(f"    ... and {len(result.errors) - 5} more")

            return True
        else:
            print(f"✗ Import failed!")
            for error in result.errors:
                print(f"  Row {error.row}, {error.column}: {error.error}")
            return False
    finally:
        db.close()


def reset_database():
    """Drop all tables and recreate them."""
    from app.core.database import Base, engine

    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("✓ Tables dropped")

    print("Recreating tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Tables recreated")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Database seeding utility")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset database before seeding"
    )
    parser.add_argument(
        "--file",
        type=str,
        help="Path to Excel file (default: data/FSD_deliverable_dataset.xlsx)"
    )

    args = parser.parse_args()

    if args.reset:
        reset_database()

    success = seed_database(args.file)
    sys.exit(0 if success else 1)
