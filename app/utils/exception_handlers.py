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
    async def global_exception_handler(request: Request, exc: Exception):
        """Handles all unexpected exceptions

        Args:
            request: The FastAPI request object
            exc: The exception that was raised

        Returns:
            JSONResponse with a 500 status code and error message
        """
        logger.error(f"Unhandled exception: {exc}", exc_info=True)  # Logs exception
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Internal Server Error. Please try again later."},
        )

    @app.exception_handler(DatabaseEntryNotFoundException)
    async def db_entry_not_found_error_handler(request: Request, exc: DatabaseEntryNotFoundException):
        """Handles invalid tuning parameter exceptions

        Args:
            request: The FastAPI request object
            exc: The TuningParameterError that was raised

        Returns:
            JSONResponse with a 400 status code and the exception message
        """

        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content={"error": str(exc)}
        )

    @app.exception_handler(DatabaseConnectionException)
    async def db_connection_error_handler(request: Request, exc: DatabaseConnectionException):
        """Handles invalid tuning parameter exceptions

        Args:
            request: The FastAPI request object
            exc: The TuningParameterError that was raised

        Returns:
            JSONResponse with a 400 status code and the exception message
        """

        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content={"error": str(exc)}
        )
