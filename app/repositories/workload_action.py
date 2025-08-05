"""
CRUD operations for WorkloadAction model.

This module provides functions to create, read, update, and delete workload actions
in the database. It handles database interactions using SQLAlchemy and includes error
handling for common database exceptions.
"""

from typing import Any, Optional, Sequence, Dict
import logging

from sqlalchemy import and_, select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, OperationalError

from app.metrics.helper import record_workload_action_metrics
from app.models.workload_action import WorkloadAction
from app.schemas.workload_action_schema import (
    WorkloadActionCreate,
    WorkloadActionUpdate,
)
from app.utils.exceptions import (
    DBEntryCreationException,
    DBEntryDeletionException,
    DBEntryUpdateException,
    DatabaseConnectionException,
    DBEntryNotFoundException,
    OrchestrationBaseException,
)

logger = logging.getLogger(__name__)

async def get_custom_DBEntryNotFoundException(
    action_id: int
) -> DBEntryNotFoundException:
    """
    Create a custom DBEntryNotFoundException for a workload action.

    Args:
        action_id (int): The ID of the workload action that was not found

    Returns:
        DBEntryNotFoundException: The custom exception
    """
    return DBEntryNotFoundException(
        f"Workload action with ID {action_id} not found"
    )


async def create_workload_action(
    db: AsyncSession,
    workload_action: WorkloadActionCreate,
    metrics_details: Dict[str, Any]
) -> WorkloadAction:
    """
    Create a new workload action in the database.

    Args:
        db (AsyncSession): Database session
        workload_action (WorkloadActionCreate): The workload action data to create

    Returns:
        WorkloadAction: The created workload action object

    Raises:
        DBEntryCreationException: If there's a database error during creation
    """
    try:
        logger.debug(
            "Creating workload action with data: %s", workload_action.model_dump()
        )
        db_workload_action = WorkloadAction(**workload_action.model_dump())
        db.add(db_workload_action)
        await db.commit()
        await db.refresh(db_workload_action)
        logger.debug("Added workload action to session")
        record_workload_action_metrics(
            metrics_details=metrics_details,
            status_code=200,
        )
        return db_workload_action

    except IntegrityError as e:
        logger.error("Integrity error while creating workload action: %s", str(e))
        await db.rollback()
        raise DBEntryCreationException(
            "Invalid workload action data", details={"error": str(e)}
        ) from e
    except OperationalError as e:
        logger.error("Operational error while creating workload action: %s", str(e))
        await db.rollback()
        raise DBEntryCreationException(
            "Database connection error", details={"error": str(e)}
        ) from e
    except SQLAlchemyError as e:
        logger.error("Database error while creating workload action: %s", str(e))
        await db.rollback()
        raise DBEntryCreationException(
            "Failed to create workload action", details={"error": str(e)}
        ) from e
    finally:
        record_workload_action_metrics(
            metrics_details=metrics_details,
            status_code=400,  # All above exceptions are thrown with 400 status code
            exception=e
        )


async def get_workload_action_by_id(
    db: AsyncSession, action_id: int, metrics_details: Dict[str, Any]
) -> Optional[WorkloadAction]:
    """
    Retrieve a workload action by its ID.

    Args:
        db (AsyncSession): Database session
        action_id (int): The ID of the workload action to retrieve

    Returns:
        Optional[WorkloadAction]: The workload action object if found, otherwise None

    Raises:
        OrchestrationBaseException: If there's a database error
    """
    try:
        logger.debug("Retrieving workload action with ID: %d", action_id)
        result = await db.execute(
            select(WorkloadAction).where(WorkloadAction.id == action_id)
        )
        workload_action = result.scalar_one_or_none()
        if not workload_action:
            custom_exception = get_custom_DBEntryNotFoundException(action_id)
            record_workload_action_metrics(
                metrics_details=metrics_details,
                status_code=404,  # Not found
                exception=custom_exception
            )
            raise custom_exception
        record_workload_action_metrics(
            metrics_details=metrics_details,
            status_code=200,  # Explicitly set
        )
        return workload_action

    except OperationalError as e:
        logger.error("Operational error while retrieving workload action: %s", str(e))
        raise OrchestrationBaseException(
            "Database connection error", details={"error": str(e)}
        ) from e
    except SQLAlchemyError as e:
        logger.error("Database error while retrieving workload action: %s", str(e))
        raise OrchestrationBaseException(
            "Failed to retrieve workload action", details={"error": str(e)}
        ) from e
    finally:
        record_workload_action_metrics(
            metrics_details=metrics_details,
            status_code=500,
            exception=e
        )


async def update_workload_action(
    db: AsyncSession, action_id: int, workload_action_update: WorkloadActionUpdate, metrics_details: Dict[str, Any]
) -> Optional[WorkloadAction]:
    """
    Update an existing workload action.

    Args:
        db (AsyncSession): Database session
        action_id (int): The ID of the workload action to update
        workload_action_update (WorkloadActionUpdate): The updated data

    Returns:
        Optional[WorkloadAction]: The updated workload action object if found, otherwise None

    Raises:
        DatabaseConnectionException: If there's a database error
    """
    try:
        logger.debug("Updating workload action with ID: %d", action_id)
        result = await db.execute(
            select(WorkloadAction).where(WorkloadAction.id == action_id)
        )
        workload_action = result.scalar_one_or_none()

        if not workload_action:
            custom_exception = get_custom_DBEntryNotFoundException(action_id)
            record_workload_action_metrics(
                metrics_details=metrics_details,
                status_code=404,  # Not found
                exception=custom_exception
            )
            raise custom_exception

        for key, value in workload_action_update.model_dump(exclude_unset=True).items():
            setattr(workload_action, key, value)

        await db.commit()
        await db.refresh(workload_action)
        logger.debug("Updated workload action with ID: %d", action_id)
        record_workload_action_metrics(
            metrics_details=metrics_details,
            status_code=200,
        )
        return workload_action

    except IntegrityError as e:
        logger.error("Integrity error while updating workload action: %s", str(e))
        await db.rollback()
        raise DBEntryUpdateException(
            "Invalid workload action data", details={"error": str(e)}
        ) from e
    except OperationalError as e:
        logger.error("Operational error while updating workload action: %s", str(e))
        await db.rollback()
        raise DBEntryUpdateException(
            "Database connection error", details={"error": str(e)}
        ) from e
    except SQLAlchemyError as e:
        logger.error("Database error while updating workload action: %s", str(e))
        await db.rollback()
        raise DBEntryUpdateException(
            "Failed to update workload action", details={"error": str(e)}
        ) from e
    finally:
        record_workload_action_metrics(
            metrics_details=metrics_details,
            status_code=400,  # All above exceptions are thrown with 400 status code
            exception=e
        )


async def delete_workload_action(
    db: AsyncSession, action_id: int, metrics_details: Dict[str, Any]
) -> Optional[WorkloadAction]:
    """
    Delete a workload action by its ID.

    Args:
        db (AsyncSession): Database session
        action_id (int): The ID of the workload action to delete

    Returns:
        Optional[WorkloadAction]: The deleted workload action object if found, otherwise None

    Raises:
        DatabaseConnectionException: If there's a database error
    """
    try:
        logger.debug("Deleting workload action with ID: %d", action_id)
        result = await db.execute(
            select(WorkloadAction).where(WorkloadAction.id == action_id)
        )
        workload_action = result.scalar_one_or_none()

        if not workload_action:
            custom_exception = get_custom_DBEntryNotFoundException(action_id)
            record_workload_action_metrics(
                metrics_details=metrics_details,
                status_code=404,  # Not found
            )
            raise custom_exception

        await db.delete(workload_action)
        await db.commit()
        logger.debug("Deleted workload action with ID: %d", action_id)
        record_workload_action_metrics(
            metrics_details=metrics_details,
            status_code=200,  # Explicitly set
        )
        return workload_action

    except IntegrityError as e:
        logger.error("Integrity error while deleting workload action: %s", str(e))
        await db.rollback()
        raise DBEntryDeletionException(
            "Failed to delete workload action due to integrity error",
            details={"error": str(e)},
        ) from e
    except OperationalError as e:
        logger.error("Operational error while deleting workload action: %s", str(e))
        await db.rollback()
        raise DBEntryDeletionException(
            "Database connection error", details={"error": str(e)}
        ) from e
    except SQLAlchemyError as e:
        logger.error("Database error while deleting workload action: %s", str(e))
        await db.rollback()
        raise DBEntryDeletionException(
            "Failed to delete workload action", details={"error": str(e)}
        ) from e
    finally:
        record_workload_action_metrics(
            metrics_details=metrics_details,
            status_code=400,
            exception=e
        )


async def list_workload_actions(
    db: AsyncSession,
    metrics_details: Dict[str, Any],
    filters: Optional[Dict[str, Any]] = None
) -> Sequence[WorkloadAction]:
    """
    List workload actions with optional filters.

    Args:
        db (AsyncSession): Database session
        filters (Optional[Dict[str, Any]]): Dictionary of filters to apply

    Returns:
        Sequence[WorkloadAction]: List of workload actions matching the filters

    Raises:
        DatabaseConnectionException: If there's a database error
    """
    try:
        query = select(WorkloadAction).order_by(desc(WorkloadAction.action_start_time))
        filter_clauses = []

        if filters:
            filter_map = {
                "action_type": WorkloadAction.action_type,
                "action_status": WorkloadAction.action_status,
                "action_reason": WorkloadAction.action_reason,
                "pod_parent_name": WorkloadAction.pod_parent_name,
                "pod_parent_type": WorkloadAction.pod_parent_type,
                "pod_parent_uid": WorkloadAction.pod_parent_uid,
                "created_pod_name": WorkloadAction.created_pod_name,
                "created_pod_namespace": WorkloadAction.created_pod_namespace,
                "created_node_name": WorkloadAction.created_node_name,
                "deleted_pod_name": WorkloadAction.deleted_pod_name,
                "deleted_pod_namespace": WorkloadAction.deleted_pod_namespace,
                "deleted_node_name": WorkloadAction.deleted_node_name,
                "bound_pod_name": WorkloadAction.bound_pod_name,
                "bound_pod_namespace": WorkloadAction.bound_pod_namespace,
                "bound_node_name": WorkloadAction.bound_node_name,
            }
            for key, column in filter_map.items():
                if filters.get(key) is not None:
                    filter_clauses.append(column == filters[key])
            if filters.get("action_start_time") is not None:
                filter_clauses.append(
                    WorkloadAction.action_start_time >= filters["action_start_time"]
                )
            if filters.get("action_end_time") is not None:
                filter_clauses.append(
                    WorkloadAction.action_end_time <= filters["action_end_time"]
                )

        if filter_clauses:
            query = query.where(and_(*filter_clauses))

        result = await db.execute(query)
        workload_actions = result.scalars().all()
        record_workload_action_metrics(
            metrics_details=metrics_details,
            status_code=200,  # Explicitly set
        )
        return workload_actions

    except SQLAlchemyError as e:
        logger.error("Database error while listing workload actions: %s", str(e))
        raise DatabaseConnectionException(
            "Failed to list workload actions", details={"error": str(e)}
        ) from e
    finally:
        record_workload_action_metrics(
            metrics_details=metrics_details,
            status_code=503,
            exception=e
        )
