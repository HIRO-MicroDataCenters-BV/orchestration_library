"""
Custom exceptions for the application.

This module defines custom exception classes for handling various error scenarios
in the application, particularly for database operations.
"""

from typing import Any, Dict, Optional
from starlette import status


class DataBaseException(Exception):
    """
    Base exception class for database-related errors.
    
    This class serves as the base for all database-related exceptions in the application.
    It provides a consistent interface for error messages, status codes, and additional details.
    """

    def __init__(
            self,
            message: str,
            status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
            details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the database exception.

        Args:
            message (str): A human-readable error message.
            status_code (int): HTTP status code for the error. Defaults to 500.
            details (Optional[Dict[str, Any]]): Additional error details. Defaults to None.
        """
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class DBEntryNotFoundException(DataBaseException):
    """
    Exception raised when a database entry is not found.
    
    This exception is used when attempting to retrieve, update, or delete
    a database entry that does not exist.
    """

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize the not found exception.

        Args:
            message (str): A human-readable error message.
            details (Optional[Dict[str, Any]]): Additional error details. Defaults to None.
        """
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            details=details
        )


class DBEntryCreationException(DataBaseException):
    """
    Exception raised when there's an error creating a database entry.
    
    This exception is used when attempting to create a new database entry
    fails due to validation errors, constraint violations, or other issues.
    """

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize the creation exception.

        Args:
            message (str): A human-readable error message.
            details (Optional[Dict[str, Any]]): Additional error details. Defaults to None.
        """
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details
        )


class DBEntryUpdateException(DataBaseException):
    """
    Exception raised when there's an error updating a database entry.
    
    This exception is used when attempting to update an existing database entry
    fails due to validation errors, constraint violations, or other issues.
    """

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize the update exception.

        Args:
            message (str): A human-readable error message.
            details (Optional[Dict[str, Any]]): Additional error details. Defaults to None.
        """
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details
        )


class DBEntryDeletionException(DataBaseException):
    """
    Exception raised when there's an error deleting a database entry.
    
    This exception is used when attempting to delete a database entry
    fails due to foreign key constraints, permission issues, or other problems.
    """

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize the deletion exception.

        Args:
            message (str): A human-readable error message.
            details (Optional[Dict[str, Any]]): Additional error details. Defaults to None.
        """
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details
        )


class DatabaseConnectionException(DataBaseException):
    """
    Exception raised when there's a database connection error.
    
    This exception is used when there are issues connecting to the database
    or when the database is temporarily unavailable.
    """

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize the connection exception.

        Args:
            message (str): A human-readable error message.
            details (Optional[Dict[str, Any]]): Additional error details. Defaults to None.
        """
        super().__init__(
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details=details
        )
