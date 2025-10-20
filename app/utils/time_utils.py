"""
Utility functions for time-related operations.
"""

from datetime import datetime

def get_ts(dt_obj: datetime) -> float:
    """Convert datetime to float timestamp with microsecond precision."""
    if dt_obj is None:
        return None
    return dt_obj.timestamp()  # float with microseconds

def ms_diff(start, end):
    """Return duration in milliseconds (float, no rounding)."""
    if start is None or end is None:
        return None
    return (end - start) * 1000.0
