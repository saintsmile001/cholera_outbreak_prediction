"""
Utility helper functions.

General-purpose functions that don't belong to a specific domain layer.
"""

from __future__ import annotations

import calendar
from datetime import datetime, timezone


def current_utc_iso() -> str:
    """Return the current UTC timestamp in ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat()


def month_name(month: int) -> str:
    """Return the abbreviated month name for a month number (1-12)."""
    if 1 <= month <= 12:
        return calendar.month_abbr[month]
    return "Unknown"


def clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    """Clamp *value* to the [lo, hi] range."""
    return max(lo, min(value, hi))


def percentage(value: float, decimals: int = 1) -> str:
    """Format a 0-1 float as a percentage string."""
    return f"{value * 100:.{decimals}f}%"
