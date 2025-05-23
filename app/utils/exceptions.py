"""
Custom exceptions for the application.

This module defines custom exception classes for handling various error scenarios
in the application, particularly for tuning parameters.
"""

from typing import Any, Dict, Optional


class DataBaseException(Exception):
    """Base exception class for DB related errors."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class DatabaseEntryNotFoundException(DataBaseException):
    """Exception raised when a db entry is not found."""

    def __init__(self, db_id: Optional[int] = None):
        message = "DB entry not found"
        if db_id is not None:
            message = f"DB entry with ID {db_id} not found"
        super().__init__(
            message=message,
            status_code=404,
            details=(
                {"id": db_id} if db_id is not None else None
            ),
        )


class DatabaseConnectionException(DataBaseException):
    """Exception raised when there's a database error related to DB connection."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, status_code=500, details=details)
