"""
Exception handlers for the application.

This module provides global exception handlers for handling various types of errors
that may occur during request processing. It includes handlers for:
- General exceptions (unexpected errors)
- Database-related exceptions (DataBaseException and its subclasses)

The handlers ensure consistent error responses and proper logging across the application.
"""

import logging
from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse
from starlette import status
from app.utils.exceptions import K8sAPIException

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
            JSONResponse with a 500 status code and a generic error message
        """
        logger.error("Unhandled exception: %s", exc, exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
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
            JSONResponse with the status code and error message from the database exception
        """
        logger.error("DataBase exception: %s", exc, exc_info=False)
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "message": exc.message
            }
        )

    @app.exception_handler(K8sAPIException)
    async def k8s_api_exception_handler(_: Request, exc: K8sAPIException):
        """
        Handle exceptions raised while interacting with Kubernetes API.
        """
        logger.error("Kubernetes API exception: %s", exc.message, exc_info=False)
        return JSONResponse(
            status_code=exc.status_code,
            content={"message": exc.message, "details": exc.details}
        )
