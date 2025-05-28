"""
Exception handlers for the application.
This module provides global exception handlers for handling various types of errors
that may occur during request processing.
"""

import logging
from fastapi import Request, FastAPI, HTTPException
from starlette import status

from app.utils.exceptions import DatabaseEntryNotFoundException, DatabaseConnectionException, DBEntryCreationException

# Configure logger
logger = logging.getLogger("uvicorn.error")


def init_exception_handlers(app: FastAPI):
    """Register global exception handlers"""

    @app.exception_handler(Exception)
    async def global_exception_handler(_: Request, exc: Exception):
        """Handles all unexpected exceptions

        Args:
            _: The FastAPI request object (unused)
            exc: The exception that was raised

        Returns:
            JSONResponse with a 500 status code and error message
        """
        logger.error("Unhandled exception: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "details": "Internal Server Error. Please try again later."
            }
        )

    @app.exception_handler(DatabaseEntryNotFoundException)
    async def db_entry_not_found_error_handler(_: Request, exc: DatabaseEntryNotFoundException):
        """Handles database entry not found exceptions

        Args:
            _: The FastAPI request object (unused)
            exc: The DatabaseEntryNotFoundException that was raised

        Returns:
            JSONResponse with a 400 status code and the exception message
        """
        raise HTTPException(
            status_code=exc.status_code,
            detail={
                "message": exc.message,
                "details": exc.details
            }
        )

    @app.exception_handler(DatabaseConnectionException)
    async def db_connection_error_handler(_: Request, exc: DatabaseConnectionException):
        """Handles database connection exceptions

        Args:
            _: The FastAPI request object (unused)
            exc: The DatabaseConnectionException that was raised

        Returns:
            JSONResponse with a 400 status code and the exception message
        """
        raise HTTPException(
            status_code=exc.status_code,
            detail={
                "message": exc.message,
                "details": exc.details
            }
        )

    @app.exception_handler(DBEntryCreationException)
    async def db_entry_creation_exception_handler(_: Request, exc: DBEntryCreationException):
        """Handles database entry creation exceptions

        Args:
            _: The FastAPI request object (unused)
            exc: The DBEntryCreationException that was raised

        Returns:
            HTTPException with appropriate status code and error details
        """
        raise HTTPException(
            status_code=exc.status_code,
            detail={
                "message": exc.message,
                "details": exc.details
            }
        )
