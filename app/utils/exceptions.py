"""
Custom exceptions for the application.

This module defines custom exception classes for handling various error scenarios
in the application, particularly for database operations.
"""

from typing import Any, Dict, Optional
from starlette import status


class OrchestrationBaseException(Exception):
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


class DBEntryNotFoundException(OrchestrationBaseException):
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
            message=message, status_code=status.HTTP_404_NOT_FOUND, details=details
        )


class DBEntryCreationException(OrchestrationBaseException):
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
            message=message, status_code=status.HTTP_400_BAD_REQUEST, details=details
        )


class DBEntryUpdateException(OrchestrationBaseException):
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
            message=message, status_code=status.HTTP_400_BAD_REQUEST, details=details
        )


class DBEntryDeletionException(OrchestrationBaseException):
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
            message=message, status_code=status.HTTP_400_BAD_REQUEST, details=details
        )


class DatabaseConnectionException(OrchestrationBaseException):
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
            details=details,
        )


class K8sAPIException(OrchestrationBaseException):
    """Exception raised for errors in Kubernetes API operations.

    This exception is used to indicate that an error occurred while interacting
    with the Kubernetes API, such as when a resource is not found or when there
    are permission issues.
    """

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize the Kubernetes API exception.

        Args:
            message (str): A human-readable error message.
            details (Optional[Dict[str, Any]]): Additional error details. Defaults to None.
        """
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details,
        )


class K8sValueError(OrchestrationBaseException):
    """Exception raised for value errors in Kubernetes operations.

    This exception is used to indicate that a value provided to a Kubernetes operation
    is invalid or not acceptable.
    """

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize the Kubernetes value error.

        Args:
            message (str): A human-readable error message.
            details (Optional[Dict[str, Any]]): Additional error details. Defaults to None.
        """
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details,
        )


class K8sTypeError(OrchestrationBaseException):
    """Exception raised for type errors in Kubernetes operations.

    This exception is used to indicate that a type mismatch occurred in a Kubernetes operation,
    such as when an expected type does not match the provided value.
    """

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize the Kubernetes type error.

        Args:
            message (str): A human-readable error message.
            details (Optional[Dict[str, Any]]): Additional error details. Defaults to None.
        """
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details,
        )


class K8sConfigException(OrchestrationBaseException):
    """Exception raised for errors in Kubernetes configuration.

    This exception is used to indicate that there is an issue with the Kubernetes configuration,
    such as when the configuration file is missing or invalid.
    """

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize the Kubernetes configuration exception.

        Args:
            message (str): A human-readable error message.
            details (Optional[Dict[str, Any]]): Additional error details. Defaults to None.
        """
        super().__init__(
            message=message, status_code=status.HTTP_403_FORBIDDEN, details=details
        )


class PostCreateAlertActionException(OrchestrationBaseException):
    """
    Raised when post-create alert actions (pod delete / resource update) fail.
    """
