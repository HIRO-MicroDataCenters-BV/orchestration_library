"""
CRUD operations for managing tuning parameters in the database.
"""

from typing import Any, Dict, Sequence
import logging

from sqlalchemy import select, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from app.metrics.helper import record_tuning_parameters_metrics
from app.models.tuning_parameter import TuningParameter
from app.schemas.tuning_parameter_schema import TuningParameterCreate
from app.utils.exceptions import DatabaseConnectionException, DBEntryNotFoundException

logger = logging.getLogger(__name__)


async def create_tuning_parameter(
    db: AsyncSession,
    tuning_parameter: TuningParameterCreate,
    metrics_details: Dict[str, Any],
) -> TuningParameter:
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
    exception = None
    try:
        logger.debug(
            "Creating tuning parameter with data: %s", tuning_parameter.model_dump()
        )
        db_tuning_parameter = TuningParameter(**tuning_parameter.model_dump())
        db.add(db_tuning_parameter)
        await db.commit()
        await db.refresh(db_tuning_parameter)
        logger.debug("Added tuning parameter to session")
        record_tuning_parameters_metrics(
            metrics_details=metrics_details,
            status_code=200
        )
        return db_tuning_parameter

    except IntegrityError as e:
        exception = e
        logger.error("Integrity error while creating tuning parameter: %s", str(e))
        await db.rollback()
        raise DatabaseConnectionException(
            "Invalid tuning parameter data", details={"error": str(e)}
        ) from e
    except SQLAlchemyError as e:
        exception = e
        logger.error("Database error while creating tuning parameter: %s", str(e))
        await db.rollback()
        raise DatabaseConnectionException(
            "Failed to create tuning parameter", details={"error": str(e)}
        ) from e
    except Exception as e:
        exception = e
        logger.error("Unexpected error while creating tuning parameter: %s", str(e))
        await db.rollback()
        raise DatabaseConnectionException(
            "An unexpected error occurred while creating tuning parameter",
            details={"error": str(e)},
        ) from e
    finally:
        record_tuning_parameters_metrics(
            metrics_details=metrics_details,
            status_code=503,
            exception=exception
        )


async def get_tuning_parameters(
    db: AsyncSession,
    tuning_parameter_reqest_args: Dict[str, Any] = None,
    metrics_details: Dict[str, Any] = None
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
        DatabaseConnectionException: If there's a database error
    """
    exception = None
    try:
        if tuning_parameter_reqest_args is None:
            tuning_parameter_reqest_args = {}
        skip = tuning_parameter_reqest_args.get("skip", 0)
        limit = tuning_parameter_reqest_args.get("limit", 100)
        start_date = tuning_parameter_reqest_args.get("start_date", None)
        end_date = tuning_parameter_reqest_args.get("end_date", None)
        logger.debug(
            "Retrieving tuning parameters with skip=%d, limit=%d, start_date=%s, end_date=%s",
            skip,
            limit,
            start_date,
            end_date,
        )
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
        logger.info("Retrieved %d tuning parameters", len(tuning_parameters))
        record_tuning_parameters_metrics(
            metrics_details=metrics_details,
            status_code=200
        )
        return tuning_parameters
    except SQLAlchemyError as e:
        exception = e
        logger.error("Database error while retrieving tuning parameters: %s", str(e))
        raise DatabaseConnectionException(
            "Failed to retrieve tuning parameters", details={"error": str(e)}
        ) from e
    except Exception as e:
        exception = e
        logger.error("Unexpected error while retrieving tuning parameters: %s", str(e))
        raise DatabaseConnectionException(
            "An unexpected error occurred while retrieving tuning parameters",
            details={"error": str(e)},
        ) from e
    finally:
        record_tuning_parameters_metrics(
            metrics_details=metrics_details,
            status_code=503,
            exception=exception
        )


async def get_latest_tuning_parameters(
    db: AsyncSession, limit: int = 1, metrics_details: Dict[str, Any] = None
) -> Sequence[TuningParameter]:
    """
    Get the latest N tuning parameters based on creation time.

    Args:
        db: Database session
        limit: Number of latest parameters to return

    Returns:
        Sequence[TuningParameter]: List of the N most recent tuning parameters

    Raises:
        DatabaseConnectionException: If there's a database error
        DBEntryNotFoundException: If no tuning parameters are found
    """
    exception = None
    try:
        logger.debug("Retrieving latest %d tuning parameters", limit)
        query = (
            select(TuningParameter)
            .order_by(desc(TuningParameter.created_at))
            .limit(limit)
        )
        result = await db.execute(query)
        tuning_parameters = result.scalars().all()

        if not tuning_parameters:
            logger.warning("No tuning parameters found")
            raise DBEntryNotFoundException(
                message="No tuning parameters found in the database",
                details={"error_type": "not_found_error"},
            )

        logger.info("Retrieved %d latest tuning parameters", len(tuning_parameters))
        record_tuning_parameters_metrics(
            metrics_details=metrics_details,
            status_code=200
        )
        return tuning_parameters
    except SQLAlchemyError as e:
        exception = e
        logger.error(
            "Database error while retrieving latest tuning parameters: %s", str(e)
        )
        raise DatabaseConnectionException(
            "Failed to retrieve latest tuning parameters", details={"error": str(e)}
        ) from e
    except Exception as e:
        exception = e
        logger.error(
            "Unexpected error while retrieving latest tuning parameters: %s", str(e)
        )
        raise DatabaseConnectionException(
            "An unexpected error occurred while retrieving latest tuning parameters",
            details={"error": str(e)},
        ) from e
    finally:
        record_tuning_parameters_metrics(
            metrics_details=metrics_details,
            status_code=503,
            exception=exception
        )
