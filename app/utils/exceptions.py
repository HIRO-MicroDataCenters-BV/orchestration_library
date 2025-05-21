"""
Custom exceptions for the application.

This module defines custom exception classes for handling various error scenarios
in the application, particularly for tuning parameters.
"""

from typing import Any, Dict, Optional


class TuningParameterError(Exception):
    """Base exception class for tuning parameter related errors."""

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


class DatabaseEntryNotFoundException(TuningParameterError):
    """Exception raised when a tuning parameter is not found."""

    def __init__(self, parameter_id: Optional[int] = None):
        message = "Tuning parameter not found"
        if parameter_id is not None:
            message = f"Tuning parameter with ID {parameter_id} not found"
        super().__init__(
            message=message,
            status_code=404,
            details=(
                {"parameter_id": parameter_id} if parameter_id is not None else None
            ),
        )


class DatabaseConnectionException(TuningParameterError):
    """Exception raised when there's a database error related to tuning parameters."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, status_code=500, details=details)
