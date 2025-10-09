"""
CRUD operations for workload decision in the database.
"""

import logging

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.metrics.helper import (
    record_workload_timing_metrics,
)
from app.models.workload_timing import WorkloadTiming
from app.schemas.workload_timing_schema import WorkloadTimingCreate, WorkloadTimingUpdate
from app.utils.exceptions import DBEntryCreationException, OrchestrationBaseException
from app.utils.time_utils import get_ts, ms_diff

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

        wt_obj = WorkloadTiming(**data.model_dump())
        wt_obj.creation_to_ready_ms = ms_diff(
            get_ts(wt_obj.created_timestamp), get_ts(wt_obj.ready_timestamp)
        )
        wt_obj.creation_to_scheduled_ms = ms_diff(
            get_ts(wt_obj.created_timestamp), get_ts(wt_obj.scheduled_timestamp)
        )
        wt_obj.scheduled_to_ready_ms = ms_diff(
            get_ts(wt_obj.scheduled_timestamp), get_ts(wt_obj.ready_timestamp)
        )
        wt_obj.total_lifecycle_ms = ms_diff(
            get_ts(wt_obj.created_timestamp), get_ts(wt_obj.deleted_timestamp)
        )

        db_session.add(wt_obj)
        await db_session.commit()
        await db_session.refresh(wt_obj)
        logger.info("successfully created workload timing for %s", data.pod_name)
        record_workload_timing_metrics(
            metrics_details=metrics_details,
            status_code=200,
        )
        return wt_obj
    except IntegrityError as exc:
        exception = exc
        raise DBEntryCreationException(
            message=f"Failed to create workload_timing with name '{data.pod_name}'",
            details={"error": str(exception)}
        ) from exception
    except OperationalError as exc:
        exception = exc
        raise DBEntryCreationException(
            message=f"Failed to create workload_timing with name '{data.pod_name}'",
            details={"error": str(exception)}
        ) from exception
    except SQLAlchemyError as exc:
        exception = exc
        raise DBEntryCreationException(
            message=f"Failed to create workload_timing with name '{data.pod_name}'",
            details={"error": str(exception)}
        ) from exception
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
        wt_result = await db_session.execute(
            select(WorkloadTiming).offset(skip).limit(limit)
        )
        record_workload_timing_metrics(
            metrics_details=metrics_details,
            status_code=200,
        )
        return wt_result.scalars().all()
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

async def get_workload_timings(
    db_session: AsyncSession,
    pod_name: str,
    namespace: str,
    metrics_details: dict = None,
):
    """
    Retrieve all WorkloadTiming records for a specific pod and namespace.

    Args:
        db_session (AsyncSession): The async SQLAlchemy database session.
        pod_name (str): Name of the pod.
        namespace (str): Namespace of the pod.

    Returns:
        List[WorkloadTiming]: A list of workload timing ORM objects.

    Raises:
        DataBaseException: If a database error occurs during retrieval.
    """
    exception = None
    try:
        wt_result = await db_session.execute(
            select(WorkloadTiming).filter_by(pod_name=pod_name, namespace=namespace)
        )
        record_workload_timing_metrics(
            metrics_details=metrics_details,
            status_code=200,
        )
        return wt_result.scalars().all()
    except SQLAlchemyError as exc:
        exception = exc
        logger.error("Error retrieving workload timings %s", str(exc))
        raise OrchestrationBaseException(
            message="Failed to retrieve workload timings due to database error.",
            details={"error": str(exc)},
        ) from exc
    finally:
        if exception:
            record_workload_timing_metrics(
                metrics_details=metrics_details, status_code=500, exception=exception
            )

async def update_workload_timing(
    db_session: AsyncSession,
    workload_timing_id: str,
    data: WorkloadTimingUpdate,
    metrics_details: dict = None,
):
    """
    Update an existing WorkloadTiming record.

    Args:
        db_session (AsyncSession): The async SQLAlchemy database session.
        workload_timing_id (str): The ID of the workload timing to update.
        data (WorkloadTimingUpdate): The updated data for the workload timing.

    Returns:
        WorkloadTiming: The updated workload timing ORM object.

    Raises:
        OrchestrationBaseException: If the update fails due to DB errors.
    """
    exception = None
    try:
        wt_result = await db_session.execute(
            select(WorkloadTiming).filter_by(id=workload_timing_id)
        )
        wt_obj = wt_result.scalars().first()
        if not wt_obj:
            raise OrchestrationBaseException(
                message=f"WorkloadTiming with id '{workload_timing_id}' not found.",
                details={},
            )

        for key, value in data.model_dump().items():
            setattr(wt_obj, key, value)

        # Recalculate timing fields if relevant timestamps are updated
        if data.created_timestamp or data.scheduled_timestamp or data.ready_timestamp or data.deleted_timestamp:
            wt_obj.creation_to_ready_ms = ms_diff(
                get_ts(wt_obj.created_timestamp), get_ts(wt_obj.ready_timestamp)
            )
            wt_obj.creation_to_scheduled_ms = ms_diff(
                get_ts(wt_obj.created_timestamp), get_ts(wt_obj.scheduled_timestamp)
            )
            wt_obj.scheduled_to_ready_ms = ms_diff(
                get_ts(wt_obj.scheduled_timestamp), get_ts(wt_obj.ready_timestamp)
            )
            wt_obj.total_lifecycle_ms = ms_diff(
                get_ts(wt_obj.created_timestamp), get_ts(wt_obj.deleted_timestamp)
            )

        await db_session.commit()
        await db_session.refresh(wt_obj)
        logger.info("successfully updated workload timing for id %s", workload_timing_id)
        record_workload_timing_metrics(
            metrics_details=metrics_details,
            status_code=200,
        )
        return wt_obj
    except SQLAlchemyError as exc:
        exception = exc
        raise OrchestrationBaseException(
            message=f"Failed to update workload_timing with id '{workload_timing_id}'",
            details={"error": str(exception)}
        ) from exception