"""
CRUD operations for workload decision in the database.
"""

import logging

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.metrics.helper import record_workload_request_decision_metrics, record_workload_timing_metrics
from app.models.workload_timing import WorkloadTiming
from app.schemas.workload_timing_schema import WorkloadTimingCreate
from app.utils.db_utils import handle_db_exception
from app.utils.exceptions import (DBEntryCreationException,
                                  OrchestrationBaseException)

# Configure logger
logger = logging.getLogger(__name__)


async def create_workload_timing(
    db_session: AsyncSession, data: WorkloadTimingCreate, metrics_details: dict
):
    """
    Create a new WorkloadTiming record in the database.

    Args:
        db_session (AsyncSession): The async SQLAlchemy database session.
        data (WorkloadTimingCreate): The data for the new workload timing.

    Returns:
        WorkloadTiming: The created workload timing ORM object.

    Raises:
        DBEntryCreationException: If creation fails due to integrity or DB errors.
    """
    exception = None
    try:
        db_obj = WorkloadTiming(**data.model_dump())
        db_session.add(db_obj)
        await db_session.commit()
        await db_session.refresh(db_obj)
        logger.info("successfully created workload timing for %s", data.pod_name)
        record_workload_timing_metrics(
            metrics_details=metrics_details,
            status_code=200,
        )
        return db_obj
    except IntegrityError as exc:
        exception = exc
        raise DBEntryCreationException(
            message=f"Failed to create workload_timing with name '{data.pod_name}'",
            pod_name=data.pod_name,
            error=str(exc),
            error_type="workload_timing_database_integrity_error",
        )
    except OperationalError as exc:
        exception = exc
        raise DBEntryCreationException(
            message=f"Failed to create workload_timing with name '{data.pod_name}'",
            pod_name=data.pod_name,
            error=str(exc),
            error_type="workload_timing_database_operational_error",
        )
    except SQLAlchemyError as exc:
        exception = exc
        raise DBEntryCreationException(
            message=f"Failed to create workload_timing with name '{data.pod_name}'",
            pod_name=data.pod_name,
            error=str(exc),
            error_type="workload_timing_database_error",
        )
    finally:
        if exception:
            record_workload_timing_metrics(
                metrics_details=metrics_details, status_code=500, exception=exception
            )


async def get_all_workload_timings(
    db_session: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    metrics_details: dict = None,
):
    """
    Retrieve all WorkloadTiming records with pagination.

    Args:
        db_session (AsyncSession): The async SQLAlchemy database session.
        skip (int): Number of records to skip.
        limit (int): Maximum number of records to retrieve.

    Returns:
        List[WorkloadTiming]: A list of workload timing ORM objects.

    Raises:
        DataBaseException: If a database error occurs during retrieval.
    """
    exception = None
    try:
        result = await db_session.execute(
            select(WorkloadTiming).offset(skip).limit(limit)
        )
        record_workload_timing_metrics(
            metrics_details=metrics_details,
            status_code=200,
        )
        return result.scalars().all()
    except SQLAlchemyError as exc:
        exception = exc
        logger.error("Error retrieving all pod timings %s", str(exc))
        raise OrchestrationBaseException(
            message="Failed to retrieve pod timings due to database error.",
            details={"error": str(exc)},
        ) from exc
    finally:
        if exception:
            record_workload_timing_metrics(
                metrics_details=metrics_details, status_code=500, exception=exception
            )
