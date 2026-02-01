"""Shared date/time helpers for consistent "today" across the API.

Using UTC date ensures overdue and days_until_due are consistent regardless
of server timezone (e.g. in containers or cloud)."""
from datetime import date, datetime, timezone


def utc_today() -> date:
    """Return today's date in UTC. Use for overdue and date-range logic."""
    return datetime.now(timezone.utc).date()
