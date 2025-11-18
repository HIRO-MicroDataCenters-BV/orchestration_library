"""
CRUD operations for workload decision in the database.
"""

import logging

from typing import Any, Dict, Optional
from uuid import UUID

from sqlalchemy.exc import SQLAlchemyError, IntegrityError, OperationalError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, select

from app.metrics.helper import record_workload_request_decision_metrics
from app.models.workload_request_decision import WorkloadRequestDecision
from app.repositories.kpi_metrics import create_kpi_metrics
from app.schemas.kpi_metrics_schema import KPIMetricsCreate
from app.schemas.workload_request_decision_schema import (
    WorkloadRequestDecisionSchema,
    WorkloadRequestDecisionStatusUpdate,
    WorkloadRequestDecisionUpdate,
    WorkloadRequestDecisionCreate,
)
from app.utils.db_utils import handle_db_exception
from app.utils.exceptions import (
    DBEntryCreationException,
    OrchestrationBaseException,
    DBEntryUpdateException,
    DBEntryDeletionException,
    DBEntryNotFoundException,
)


# Configure logger
logger = logging.getLogger(__name__)


async def record_kpi_metrics(
    db_session: AsyncSession, wrd_obj: WorkloadRequestDecision
) -> None:
    """Record KPI metrics for a given WorkloadRequestDecision object."""
    # Safely compute decision duration in seconds
    logger.info("Recording KPI metrics for pod decision %s", wrd_obj.id)
    duration_seconds = None
    if getattr(wrd_obj, "decision_start_time", None) and getattr(
        wrd_obj, "decision_end_time", None
    ):
        delta = wrd_obj.decision_end_time - wrd_obj.decision_start_time
        duration_seconds = float(delta.total_seconds())
    if duration_seconds is not None and getattr(wrd_obj, "node_name", None):
        kpi_data = KPIMetricsCreate(
            request_decision_id=wrd_obj.id,
            node_name=wrd_obj.node_name,
            decision_time_in_seconds=duration_seconds,
        )
        await create_kpi_metrics(db_session, kpi_data, metrics_details=None)


async def create_workload_decision(
    db_session: AsyncSession, data: WorkloadRequestDecisionCreate, metrics_details: dict
):
    """
    Create a new WorkloadRequestDecision record in the database.

    Args:
        db_session (AsyncSession): The async SQLAlchemy database session.
        data (WorkloadRequestDecisionCreate): The data for the new pod decision.

    Returns:
        WorkloadRequestDecision: The created pod decision ORM object.

    Raises:
        DBEntryCreationException: If creation fails due to integrity or DB errors.
    """
    exception = None
    wrd_snapshot: Optional[WorkloadRequestDecisionSchema] = None
    db_session.expire_on_commit = False
    try:
        wrd_obj = WorkloadRequestDecision(**data.model_dump())
        db_session.add(wrd_obj)
        await db_session.commit()
        await db_session.refresh(wrd_obj)
        # Snapshot BEFORE more commits (KPI metrics) to avoid later expirations
        wrd_snapshot = WorkloadRequestDecisionSchema.model_validate(
            wrd_obj, from_attributes=True
        )
        logger.info("successfully created pod decision with %s", data.pod_name)
        record_workload_request_decision_metrics(
            metrics_details=metrics_details,
            status_code=200,
        )
        await record_kpi_metrics(db_session, wrd_obj)
        return wrd_snapshot
    except IntegrityError as exc:
        exception = exc
        await handle_db_exception(
            exc,
            db_session,
            logger,
            exception_details={
                "message": f"Failed to create workload_decision with name '{data.pod_name}'",
                "pod_name": data.pod_name,
                "error": str(exc),
                "error_type": "pod_request_decision_database_integrity_error",
            },
            custom_exception_cls=DBEntryCreationException,
        )
    except OperationalError as exc:
        exception = exc
        await handle_db_exception(
            exc,
            db_session,
            logger,
            exception_details={
                "message": f"Failed to create workload_decision with name '{data.pod_name}'",
                "pod_name": data.pod_name,
                "error": str(exc),
                "error_type": "pod_request_decision_database_connection_error",
            },
            custom_exception_cls=DBEntryCreationException,
        )
    except SQLAlchemyError as exc:
        exception = exc
        await handle_db_exception(
            exc,
            db_session,
            logger,
            exception_details={
                "message": f"Failed to create workload_decision with pod '{data.pod_name}'",
                "pod_name": data.pod_name,
                "error": str(exc),
                "error_type": "database_error",
            },
            custom_exception_cls=DBEntryCreationException,
        )
    finally:
        if exception:
            record_workload_request_decision_metrics(
                metrics_details=metrics_details, status_code=400, exception=exception
            )


async def get_workload_decision(
    db_session: AsyncSession, decision_id: UUID, metrics_details: dict
):
    """
    Retrieve a specific WorkloadRequestDecision by its ID.

    Args:
        db_session (AsyncSession): The async SQLAlchemy database session.
        decision_id (UUID): The ID of the pod decision to retrieve.

    Returns:
        WorkloadRequestDecision: The pod decision ORM object if found.

    Raises:
        DBEntryNotFoundException: If the pod decision is not found.
        DataBaseException: For database-related errors.
    """
    exception = None
    try:
        result = await db_session.execute(
            select(WorkloadRequestDecision).where(
                WorkloadRequestDecision.id == decision_id
            )
        )
        workload_decision = result.scalar_one_or_none()

        if not workload_decision:
            exception = DBEntryNotFoundException(
                message=f"Pod decision with id '{decision_id}' not found."
            )
            record_workload_request_decision_metrics(
                metrics_details=metrics_details, status_code=404, exception=exception
            )
            raise exception
        record_workload_request_decision_metrics(
            metrics_details=metrics_details,
            status_code=200,
        )
        return workload_decision
    except OperationalError as exc:
        exception = exc
        logger.error(
            "Database operational error while retrieving pod decision : %s", str(exc)
        )
        raise OrchestrationBaseException(
            message="Failed to retrieve pod decision : Database connection error",
            details={"error_type": "database_connection_error", "error": str(exc)},
        ) from exc
    except SQLAlchemyError as exc:
        exception = exc
        logger.error("Database error while retrieving pod decision : %s", str(exc))
        raise OrchestrationBaseException(
            message="Failed to retrieve pod decision: Database error",
            details={"error_type": "database_error", "error": str(exc)},
        ) from exc
    finally:
        if exception:
            record_workload_request_decision_metrics(
                metrics_details=metrics_details, status_code=500, exception=exception
            )


async def get_all_workload_decisions(
    db_session: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    filters: Optional[Dict[str, Any]] = None,
    metrics_details: dict = None,
):
    """
    Retrieve all WorkloadRequestDecision records with pagination.

    Args:
        db_session (AsyncSession): The async SQLAlchemy database session.
        skip (int): Number of records to skip.
        limit (int): Maximum number of records to retrieve.
        filters (Optional[Dict[str, Any]]): Optional filters to apply to the query.

    Returns:
        List[WorkloadRequestDecision]: A list of pod decision ORM objects.

    Raises:
        DataBaseException: If a database error occurs during retrieval.
    """
    exception = None
    try:
        query = select(WorkloadRequestDecision).offset(skip).limit(limit)
        filter_clauses = []

        if filters:
            filter_map = {
                "is_elastic": WorkloadRequestDecision.is_elastic,
                "queue_name": WorkloadRequestDecision.queue_name,
                "demand_cpu": WorkloadRequestDecision.demand_cpu,
                "demand_memory": WorkloadRequestDecision.demand_memory,
                "demand_slack_cpu": WorkloadRequestDecision.demand_slack_cpu,
                "demand_slack_memory": WorkloadRequestDecision.demand_slack_memory,
                "pod_name": WorkloadRequestDecision.pod_name,
                "namespace": WorkloadRequestDecision.namespace,
                "node_id": WorkloadRequestDecision.node_id,
                "node_name": WorkloadRequestDecision.node_name,
                "action_type": WorkloadRequestDecision.action_type,
                "decision_status": WorkloadRequestDecision.decision_status,
                "pod_parent_id": WorkloadRequestDecision.pod_parent_id,
                "pod_parent_name": WorkloadRequestDecision.pod_parent_name,
                "pod_parent_kind": WorkloadRequestDecision.pod_parent_kind,
            }
            for key, column in filter_map.items():
                if filters.get(key) is not None:
                    filter_clauses.append(column == filters[key])
            if filters.get("decision_start_time") is not None:
                filter_clauses.append(
                    WorkloadRequestDecision.decision_start_time
                    >= filters["decision_start_time"]
                )
            if filters.get("decision_end_time") is not None:
                filter_clauses.append(
                    WorkloadRequestDecision.decision_end_time
                    <= filters["decision_end_time"]
                )

        if filter_clauses:
            query = query.where(and_(*filter_clauses))

        wrd_result = await db_session.execute(query)

        record_workload_request_decision_metrics(
            metrics_details=metrics_details,
            status_code=200,
        )
        return wrd_result.scalars().all()
    except SQLAlchemyError as exc:
        exception = exc
        logger.error("Error retrieving all pod decisions %s", str(exc))
        raise OrchestrationBaseException(
            message="Failed to retrieve pod decisions due to database error.",
            details={"error": str(exc)},
        ) from exc
    finally:
        if exception:
            record_workload_request_decision_metrics(
                metrics_details=metrics_details, status_code=500, exception=exception
            )


async def update_workload_decision(
    db_session: AsyncSession,
    decision_id: UUID,
    data: WorkloadRequestDecisionUpdate,
    metrics_details: dict,
):
    """
    Update an existing WorkloadRequestDecision record by its ID.

    Args:
        db_session (AsyncSession): The async SQLAlchemy database session.
        decision_id (UUID): The ID of the pod decision to update.
        data (WorkloadRequestDecisionUpdate): Fields to update in the record.

    Returns:
        WorkloadRequestDecision: The updated pod decision ORM object.

    Raises:
        DBEntryNotFoundException: If the pod decision is not found.
        DBEntryUpdateException: If update fails due to integrity or DB errors.
    """
    exception = None
    try:
        result = await db_session.execute(
            select(WorkloadRequestDecision).where(
                WorkloadRequestDecision.id == decision_id
            )
        )
        workload_decision = result.scalar_one_or_none()

        if not workload_decision:
            exception = DBEntryNotFoundException(
                message=f"Pod decision with id '{decision_id}' not found."
            )
            record_workload_request_decision_metrics(
                metrics_details=metrics_details, status_code=404, exception=exception
            )
            raise exception

        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(workload_decision, key, value)

        await db_session.commit()
        await db_session.refresh(workload_decision)
        logger.info("Successfully updated pod decision %s", decision_id)
        record_workload_request_decision_metrics(
            metrics_details=metrics_details,
            status_code=200,
        )
        return workload_decision

    except IntegrityError as exc:
        exception = exc
        await db_session.rollback()
        logger.error(
            "Integrity error while updating pod decision %s %s",
            decision_id,
            str(exc),
        )
        raise DBEntryUpdateException(
            message="Failed to update pod decision due to integrity error.",
            details={"error": str(exc)},
        ) from exc
    except OperationalError as exc:
        exception = exc
        await db_session.rollback()
        logger.error(
            "Database operational error while updating pod decision %s: %s",
            decision_id,
            str(exc),
        )
        raise DBEntryUpdateException(
            message=f"Failed to update pod decision {decision_id}: Database connection error",
            details={
                "error_type": "database_connection_error",
                "error": str(exc),
                "decision_id": str(decision_id),
            },
        ) from exc
    except SQLAlchemyError as exc:
        exception = exc
        await db_session.rollback()
        logger.error(
            "SQL error while updating pod decision %s %s ", decision_id, str(exc)
        )
        raise DBEntryUpdateException(
            message="Failed to update pod decision due to database error.",
            details={"error": str(exc)},
        ) from exc
    finally:
        if exception:
            record_workload_request_decision_metrics(
                metrics_details=metrics_details, status_code=500, exception=exception
            )


async def update_workload_decision_status(
    db_session: AsyncSession,
    data: WorkloadRequestDecisionStatusUpdate,
    metrics_details: dict,
):
    """
    Update an existing WorkloadRequestDecision record status by its identity.

    Args:
        db_session (AsyncSession): The async SQLAlchemy database session.
        data (WorkloadRequestDecisionStatusUpdate): Fields to update in the record.

    Returns:
        WorkloadRequestDecision: The updated pod decision ORM object.

    Raises:
        DBEntryNotFoundException: If the pod decision is not found.
        DBEntryUpdateException: If update fails due to integrity or DB errors.
    """
    exception = None
    try:
        result = await db_session.execute(
            select(WorkloadRequestDecision).where(
                and_(
                    WorkloadRequestDecision.pod_name == data.pod_name,
                    WorkloadRequestDecision.namespace == data.namespace,
                    WorkloadRequestDecision.node_name == data.node_name,
                    WorkloadRequestDecision.action_type == data.action_type,
                )
            )
        )
        workload_decision = result.scalar_one_or_none()

        if not workload_decision:
            exception = DBEntryNotFoundException(
                message=(
                    f"Pod decision with identity '{data.pod_name}, "
                    f"{data.namespace}, {data.node_name}, {data.action_type}' not found."
                )
            )
            record_workload_request_decision_metrics(
                metrics_details=metrics_details, status_code=404, exception=exception
            )
            raise exception

        workload_decision.decision_status = data.decision_status

        await db_session.commit()
        await db_session.refresh(workload_decision)
        logger.info("Successfully updated pod decision status for %s", data.pod_name)
        record_workload_request_decision_metrics(
            metrics_details=metrics_details,
            status_code=200,
        )
        return workload_decision

    except IntegrityError as exc:
        exception = exc
        await db_session.rollback()
        logger.error(
            "Integrity error while updating pod decision status for %s: %s",
            data.pod_name,
            str(exc),
        )
        raise DBEntryUpdateException(
            message="Failed to update pod decision status due to integrity error.",
            details={"error": str(exc)},
        ) from exc
    except OperationalError as exc:
        exception = exc
        await db_session.rollback()
        logger.error(
            "Database operational error while updating pod decision status for %s: %s",
            data.pod_name,
            str(exc),
        )
        raise DBEntryUpdateException(
            message=(
                f"Failed to update pod decision status for {data.pod_name}: "
                "Database connection error"
            ),
            details={
                "error_type": "database_connection_error",
                "error": str(exc),
                "pod_name": str(data.pod_name),
            },
        ) from exc
    except SQLAlchemyError as exc:
        exception = exc
        await db_session.rollback()
        logger.error(
            "SQL error while updating pod decision status for %s: %s",
            data.pod_name,
            str(exc),
        )
        raise DBEntryUpdateException(
            message="Failed to update pod decision status due to database error.",
            details={"error": str(exc)},
        ) from exc
    finally:
        if exception:
            record_workload_request_decision_metrics(
                metrics_details=metrics_details, status_code=500, exception=exception
            )


async def delete_workload_decision(
    db_session: AsyncSession, decision_id: UUID, metrics_details: dict
):
    """
    Delete a WorkloadRequestDecision record by its ID.

    Args:
        db_session (AsyncSession): The async SQLAlchemy database session.
        decision_id (UUID): The ID of the pod decision to delete.

    Returns:
        bool: True if deletion is successful.

    Raises:
        DBEntryNotFoundException: If the pod decision is not found.
        DBEntryDeletionException: If deletion fails due to DB errors.
    """
    exception = None
    try:
        result = await db_session.execute(
            select(WorkloadRequestDecision).where(
                WorkloadRequestDecision.id == decision_id
            )
        )
        workload_decision = result.scalar_one_or_none()

        if not workload_decision:
            exception = DBEntryNotFoundException(
                message=f"Pod decision with id '{decision_id}' not found."
            )
            record_workload_request_decision_metrics(
                metrics_details=metrics_details, status_code=404, exception=exception
            )
            raise exception

        await db_session.delete(workload_decision)
        await db_session.commit()
        logger.info("Successfully deleted pod decision %s", decision_id)
        record_workload_request_decision_metrics(
            metrics_details=metrics_details,
            status_code=200,
        )
        return True

    except IntegrityError as exc:
        exception = exc
        await db_session.rollback()
        logger.error(
            "Integrity error while deleting pod decision %s: %s",
            decision_id,
            str(exc),
        )
        raise DBEntryDeletionException(
            message=f"Failed to delete pod decision {decision_id}: Data constraint violation",
            details={
                "error_type": "database_integrity_error",
                "error": str(exc),
                "decision_id": str(decision_id),
            },
        ) from exc
    except OperationalError as exc:
        exception = exc
        await db_session.rollback()
        logger.error(
            "Database operational error while deleting pod decision %s: %s",
            decision_id,
            str(exc),
        )
        raise DBEntryDeletionException(
            message=f"Failed to delete pod decision {decision_id}: Database connection error",
            details={
                "error_type": "database_connection_error",
                "error": str(exc),
                "decision_id": str(decision_id),
            },
        ) from exc
    except SQLAlchemyError as exc:
        exception = exc
        await db_session.rollback()
        logger.error(
            "Database error while deleting pod decision %s: %s",
            decision_id,
            str(exc),
        )
        raise DBEntryDeletionException(
            message=f"Failed to delete pod decision {decision_id}: Database error",
            details={
                "error_type": "database_error",
                "error": str(exc),
                "decision_id": str(decision_id),
            },
        ) from exc
    finally:
        if exception:
            record_workload_request_decision_metrics(
                metrics_details=metrics_details, status_code=500, exception=exception
            )
