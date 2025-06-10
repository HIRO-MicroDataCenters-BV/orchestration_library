"""
CRUD operations for managing tuning parameters in the database.
"""

import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from app.models.alerts import Alert
from app.models.tuning_parameter import TuningParameter
from app.schemas.alerts_request import AlertCreateRequest
from app.schemas.tuning_parameter_schema import TuningParameterCreate
from app.utils.exceptions import (
    DatabaseConnectionException
)

logger = logging.getLogger(__name__)


async def create_alert(
        db: AsyncSession, alert: AlertCreateRequest
) -> Alert:
    """
    Create a new tuning parameter in the database.

    Args:
        db (AsyncSession): Database session
        tuning_parameter (TuningParameterCreate): The tuning parameter data to create

    Returns:
        TuningParameter: The created tuning parameter object

    Raises:
        DatabaseConnectionException: If there's a database error
    """
    try:
        logger.debug("Creating tuning parameter with data: %s", alert.dict())
        alert_model = Alert(**alert.dict())
        db.add(alert_model)
        await db.commit()
        await db.refresh(alert_model)
        logger.debug("Added tuning parameter to session")
        return alert_model

    except IntegrityError as e:
        logger.error("Integrity error while creating tuning parameter: %s", str(e))
        await db.rollback()
        raise DatabaseConnectionException(
            "Invalid tuning parameter data",
            details={"error": str(e)}
        ) from e
    except SQLAlchemyError as e:
        logger.error("Database error while creating tuning parameter: %s", str(e))
        await db.rollback()
        raise DatabaseConnectionException(
            "Failed to create tuning parameter",
            details={"error": str(e)}
        ) from e
    except Exception as e:
        logger.error("Unexpected error while creating tuning parameter: %s", str(e))
        await db.rollback()
        raise DatabaseConnectionException(
            "An unexpected error occurred while creating tuning parameter",
            details={"error": str(e)}
        ) from e
