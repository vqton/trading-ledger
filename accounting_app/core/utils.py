"""Core database utilities."""
from datetime import datetime, timezone


def utc_now():
    """Return current UTC datetime."""
    return datetime.now(timezone.utc)
