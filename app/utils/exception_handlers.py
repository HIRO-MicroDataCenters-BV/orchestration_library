"""
Exception handlers for the application.

This module provides global exception handlers for handling various types of errors
that may occur during request processing. It includes handlers for:
- General exceptions (unexpected errors)
- Database-related exceptions (DataBaseException and its subclasses)

The handlers ensure consistent error responses and proper logging across the application.
"""

import logging
from fastapi import Request, FastAPI, HTTPException
from starlette import status

from app.utils.exceptions import DataBaseException

# Configure logger
logger = logging.getLogger("uvicorn.error")


def init_exception_handlers(app: FastAPI):
    """
    Register global exception handlers for the FastAPI application.
    
    This function sets up exception handlers that will catch and process various types
    of exceptions that may occur during request processing. The handlers ensure:
    - Consistent error response format
    - Proper error logging
    - Appropriate HTTP status codes
    """

    @app.exception_handler(Exception)
    async def global_exception_handler(_: Request, exc: Exception):
        """
        Handle all unexpected exceptions that aren't caught by more specific handlers.

        This handler catches any unhandled exceptions and returns a generic error response.
        It ensures that no unexpected errors are exposed to the client while maintaining
        proper logging for debugging purposes.

        Args:
            _: The FastAPI request object
            exc: The exception that was raised

        Returns:
            HTTPException with a 400 status code and a generic error message
        """
        logger.error("Unhandled exception: %s", exc, exc_info=False)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Internal Server Error. Please try again later."
            }
        )

    @app.exception_handler(DataBaseException)
    async def db_exception_handler(_: Request, exc: DataBaseException):
        """
        Handle database-related exceptions.

        This handler processes all database-related exceptions (DataBaseException and its
        subclasses). It ensures that database errors are properly logged and returned
        to the client with appropriate status codes and error messages.

        Args:
            _: The FastAPI request object
            exc: The DataBaseException that was raised

        Returns:
            HTTPException with the status code and error message from the database exception
        """
        raise HTTPException(
            status_code=exc.status_code,
            detail={
                "message": exc.message
            }
        )
