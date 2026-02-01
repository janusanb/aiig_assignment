"""
Pytest configuration and shared fixtures.

Uses the real database (SQLite) seeded from the Excel dataset.
Run from backend/: pytest tests/
"""
import sys
from pathlib import Path

_backend = Path(__file__).resolve().parent.parent
if str(_backend) not in sys.path:
    sys.path.insert(0, str(_backend))

import pytest
from fastapi.testclient import TestClient

from app.core.database import init_db, SessionLocal
from app.main import app


@pytest.fixture(scope="session")
def ensure_db():
    """Initialize DB and seed from Excel if empty (once per test session)."""
    init_db()
    from app.models import Project

    db = SessionLocal()
    try:
        if db.query(Project).count() == 0:
            import seed

            seed.seed_database()
    finally:
        db.close()


@pytest.fixture
def db(ensure_db):
    """Provide a DB session per test (real DB with Excel data)."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(ensure_db):
    """HTTP client for behavioral tests (real app + real DB)."""
    return TestClient(app)


def restore_db():
    """Reset database and re-seed from Excel to restore base state. Used after unit tests that create rows."""
    import seed

    seed.reset_database()
    seed.seed_database()


@pytest.fixture
def restore_db_after(request):
    """Use in unit tests that create rows in the DB; restores DB to base state after the test."""
    request.addfinalizer(restore_db)
