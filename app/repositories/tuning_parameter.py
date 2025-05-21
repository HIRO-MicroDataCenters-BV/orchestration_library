"""
CRUD operations for managing tuning parameters in the database.
"""

from datetime import datetime
from typing import Optional, Sequence
import logging

from sqlalchemy import select, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from app.models.tuning_parameter import TuningParameter
from app.schemas.tuning_parameter_schema import TuningParameterCreate
from app.utils.exceptions import (
    TuningParameterDatabaseError,
    TuningParameterNotFoundError
)

logger = logging.getLogger(__name__)


async def create_tuning_parameter(
        db: AsyncSession, tuning_parameter: TuningParameterCreate
) -> TuningParameter:
    """
    Create a new tuning parameter in the database.

    Args:
        db (AsyncSession): Database session
        tuning_parameter (TuningParameterCreate): The tuning parameter data to create

    Returns:
        TuningParameter: The created tuning parameter object

    Raises:
        TuningParameterDatabaseError: If there's a database error
    """
    try:
        logger.debug(f"Creating tuning parameter with data: {tuning_parameter.dict()}")
        db_tuning_parameter = TuningParameter(**tuning_parameter.dict())
        db.add(db_tuning_parameter)
        await db.commit()
        await db.refresh(db_tuning_parameter)
        logger.debug("Added tuning parameter to session")
        return db_tuning_parameter

    except IntegrityError as e:
        logger.error(f"Integrity error while creating tuning parameter: {str(e)}")
        await db.rollback()
        raise TuningParameterDatabaseError(
            "Invalid tuning parameter data",
            details={"error": str(e)}
        )
    except SQLAlchemyError as e:
        logger.error(f"Database error while creating tuning parameter: {str(e)}")
        await db.rollback()
        raise TuningParameterDatabaseError(
            "Failed to create tuning parameter",
            details={"error": str(e)}
        )
    except Exception as e:
        logger.error(f"Unexpected error while creating tuning parameter: {str(e)}")
        await db.rollback()
        raise TuningParameterDatabaseError(
            "An unexpected error occurred while creating tuning parameter",
            details={"error": str(e)}
        )


async def get_tuning_parameters(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
) -> Sequence[TuningParameter]:
    """
    Get a list of tuning parameters with pagination and optional date filtering.

    Args:
        db (AsyncSession): Database session
        skip (int): Number of records to skip (default: 0)
        limit (int): Maximum number of records to return (default: 100)
        start_date (Optional[datetime]): Filter records created after this date
        end_date (Optional[datetime]): Filter records created before this date

    Returns:
        Sequence[TuningParameter]: List of tuning parameters matching the criteria

    Raises:
        TuningParameterDatabaseError: If there's a database error
    """
    try:
        logger.debug(
            f"Retrieving tuning parameters with skip={skip}, limit={limit}, start_date={start_date}, end_date={end_date}")
        query = select(TuningParameter)

        if start_date or end_date:
            conditions = []
            if start_date:
                conditions.append(TuningParameter.created_at >= start_date)
            if end_date:
                conditions.append(TuningParameter.created_at <= end_date)
            if conditions:
                query = query.where(and_(*conditions))

        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        tuning_parameters = result.scalars().all()
        logger.info(f"Retrieved {len(tuning_parameters)} tuning parameters")
        return tuning_parameters
    except SQLAlchemyError as e:
        logger.error(f"Database error while retrieving tuning parameters: {str(e)}")
        raise TuningParameterDatabaseError(
            "Failed to retrieve tuning parameters",
            details={"error": str(e)}
        )
    except Exception as e:
        logger.error(f"Unexpected error while retrieving tuning parameters: {str(e)}")
        raise TuningParameterDatabaseError(
            "An unexpected error occurred while retrieving tuning parameters",
            details={"error": str(e)}
        )


async def get_latest_tuning_parameters(
        db: AsyncSession, limit: int = 1
) -> Sequence[TuningParameter]:
    """
    Get the latest N tuning parameters based on creation time.

    Args:
        db: Database session
        limit: Number of latest parameters to return

    Returns:
        Sequence[TuningParameter]: List of the N most recent tuning parameters

    Raises:
        TuningParameterDatabaseError: If there's a database error
        TuningParameterNotFoundError: If no tuning parameters are found
    """
    try:
        logger.debug(f"Retrieving latest {limit} tuning parameters")
        query = (
            select(TuningParameter).order_by(desc(TuningParameter.created_at)).limit(limit)
        )
        result = await db.execute(query)
        tuning_parameters = result.scalars().all()

        if not tuning_parameters:
            logger.warning("No tuning parameters found")
            raise TuningParameterNotFoundError()

        logger.info(f"Retrieved {len(tuning_parameters)} latest tuning parameters")
        return tuning_parameters
    except SQLAlchemyError as e:
        logger.error(f"Database error while retrieving latest tuning parameters: {str(e)}")
        raise TuningParameterDatabaseError(
            "Failed to retrieve latest tuning parameters",
            details={"error": str(e)}
        )
    except Exception as e:
        logger.error(f"Unexpected error while retrieving latest tuning parameters: {str(e)}")
        raise TuningParameterDatabaseError(
            "An unexpected error occurred while retrieving latest tuning parameters",
            details={"error": str(e)}
        )
