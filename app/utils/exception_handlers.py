"""
Exception handlers for the application.
This module provides global exception handlers for handling various types of errors
that may occur during request processing.
"""

import logging
from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse
from starlette import status

from app.utils.exceptions import DatabaseEntryNotFoundException, DatabaseConnectionException

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
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Internal Server Error. Please try again later."},
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
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content={"error": str(exc)}
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
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content={"error": str(exc)}
        )
