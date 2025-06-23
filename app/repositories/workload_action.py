"""
CRUD operations for WorkloadAction model.

This module provides functions to create, read, update, and delete workload actions
in the database. It handles database interactions using SQLAlchemy and includes error
handling for common database exceptions.
"""
from datetime import datetime, timezone
from math import e
from typing import Optional, Sequence
import logging

from sqlalchemy import select, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, OperationalError

from app.models.workload_action import WorkloadAction
from app.schemas.workload_action_schema import WorkloadActionCreate, WorkloadActionUpdate
from app.utils.exceptions import DBEntryCreationException, DBEntryDeletionException, DBEntryUpdateException, DatabaseConnectionException, DBEntryNotFoundException

logger = logging.getLogger(__name__)


async def create_workload_action(
        db: AsyncSession, workload_action: WorkloadActionCreate
) -> WorkloadAction:
    """
    Create a new workload action in the database.

    Args:
        db (AsyncSession): Database session
        workload_action (WorkloadActionCreate): The workload action data to create

    Returns:
        WorkloadAction: The created workload action object

    Raises:
        DatabaseConnectionException: If there's a database error
    """
    try:
        logger.debug("Creating workload action with data: %s", workload_action.model_dump())
        db_workload_action = WorkloadAction(**workload_action.model_dump())
        db.add(db_workload_action)
        await db.commit()
        await db.refresh(db_workload_action)
        logger.debug("Added workload action to session")
        return db_workload_action

    except IntegrityError as e:
        logger.error("Integrity error while creating workload action: %s", str(e))
        await db.rollback()
        raise DBEntryCreationException(
            "Invalid workload action data",
            details={"error": str(e)}
        ) from e
    except OperationalError as e:
        logger.error("Operational error while creating workload action: %s", str(e))
        await db.rollback()
        raise DBEntryCreationException(
            "Database connection error",
            details={"error": str(e)}
        ) from e
    except SQLAlchemyError as e:
        logger.error("Database error while creating workload action: %s", str(e))
        await db.rollback()
        raise DBEntryCreationException(
            "Failed to create workload action",
            details={"error": str(e)}
        ) from e


async def get_workload_action_by_id(
        db: AsyncSession, action_id: int
) -> Optional[WorkloadAction]:
    """
    Retrieve a workload action by its ID.

    Args:
        db (AsyncSession): Database session
        action_id (int): The ID of the workload action to retrieve

    Returns:
        Optional[WorkloadAction]: The workload action object if found, otherwise None

    Raises:
        DatabaseConnectionException: If there's a database error
    """
    try:
        logger.debug("Retrieving workload action with ID: %d", action_id)
        result = await db.execute(select(WorkloadAction).where(WorkloadAction.id == action_id))
        workload_action = result.scalar_one_or_none()
        if not workload_action:
            raise DBEntryNotFoundException(
                f"Workload action with ID {action_id} not found"
            )
        return workload_action

    except OperationalError as e:
        logger.error("Operational error while retrieving workload action: %s", str(e))
        raise BaseException(
            "Database connection error",
            details={"error": str(e)}
        ) from e
    except SQLAlchemyError as e:
        logger.error("Database error while retrieving workload action: %s", str(e))
        raise BaseException(
            "Failed to retrieve workload action",
            details={"error": str(e)}
        ) from e


async def update_workload_action(
        db: AsyncSession, action_id: int, workload_action_update: WorkloadActionUpdate
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
        result = await db.execute(select(WorkloadAction).where(
            WorkloadAction.action_id == action_id
        ))
        workload_action = result.scalar_one_or_none()

        if not workload_action:
            raise DBEntryNotFoundException(
                f"Workload action with ID {action_id} not found"
            )

        for key, value in workload_action_update.model_dump(exclude_unset=True).items():
            setattr(workload_action, key, value)

        await db.commit()
        await db.refresh(workload_action)
        logger.debug("Updated workload action with ID: %d", action_id)
        return workload_action

    except IntegrityError as e:
        logger.error("Integrity error while updating workload action: %s", str(e))
        await db.rollback()
        raise DBEntryUpdateException(
            "Invalid workload action data",
            details={"error": str(e)}
        ) from e
    except OperationalError as e:
        logger.error("Operational error while updating workload action: %s", str(e))
        await db.rollback()
        raise DBEntryUpdateException(
            "Database connection error",
            details={"error": str(e)}
        ) from e
    except SQLAlchemyError as e:
        logger.error("Database error while updating workload action: %s", str(e))
        await db.rollback()
        raise DBEntryUpdateException(
            "Failed to update workload action",
            details={"error": str(e)}
        ) from e


async def delete_workload_action(
        db: AsyncSession, action_id: int
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
        result = await db.execute(select(WorkloadAction).where(
            WorkloadAction.action_id == action_id
        ))
        workload_action = result.scalar_one_or_none()

        if not workload_action:
            raise DBEntryNotFoundException(
                f"Workload action with ID {action_id} not found"
            )

        await db.delete(workload_action)
        await db.commit()
        logger.debug("Deleted workload action with ID: %d", action_id)
        return workload_action

    except IntegrityError as e:
        logger.error("Integrity error while deleting workload action: %s", str(e))
        await db.rollback()
        raise DBEntryDeletionException(
            "Failed to delete workload action due to integrity error",
            details={"error": str(e)}
        ) from e
    except OperationalError as e:
        logger.error("Operational error while deleting workload action: %s", str(e))
        await db.rollback()
        raise DBEntryDeletionException(
            "Database connection error",
            details={"error": str(e)}
        ) from e
    except SQLAlchemyError as e:
        logger.error("Database error while deleting workload action: %s", str(e))
        await db.rollback()
        raise DBEntryDeletionException(
            "Failed to delete workload action",
            details={"error": str(e)}
        ) from e


async def list_workload_actions(
        db: AsyncSession,
        action_type: Optional[str] = None,
        action_status: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
) -> Sequence[WorkloadAction]:
    """
    List workload actions with optional filters.

    Args:
        db (AsyncSession): Database session
        action_type (Optional[str]): Filter by action type
        action_status (Optional[str]): Filter by action status
        start_time (Optional[datetime]): Filter by start time
        end_time (Optional[datetime]): Filter by end time

    Returns:
        Sequence[WorkloadAction]: List of workload actions matching the filters

    Raises:
        DatabaseConnectionException: If there's a database error
    """
    try:
        query = select(WorkloadAction).order_by(desc(WorkloadAction.action_start_time))

        if action_type:
            query = query.where(WorkloadAction.action_type == action_type)
        if action_status:
            query = query.where(WorkloadAction.action_status == action_status)
        if start_time:
            query = query.where(WorkloadAction.action_start_time >= start_time)
        if end_time:
            query = query.where(WorkloadAction.action_end_time <= end_time)

        logger.debug("Listing workload actions with filters: %s", {
            "action_type": action_type,
            "action_status": action_status,
            "start_time": start_time,
            "end_time": end_time
        })

        result = await db.execute(query)
        workload_actions = result.scalars().all()
        return workload_actions

    except SQLAlchemyError as e:
        logger.error("Database error while listing workload actions: %s", str(e))
        raise DatabaseConnectionException(
            "Failed to list workload actions",
            details={"error": str(e)}
        ) from e
