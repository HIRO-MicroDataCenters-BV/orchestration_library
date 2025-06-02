"""
CRUD operations for managing pods in the database.
This module provides functions to create, read, update, and delete pod records.
It uses SQLAlchemy ORM for database interactions.
"""
from dataclasses import dataclass

import logging
from uuid import UUID

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.pod import Pod
from app.schemas.pod import PodCreate, PodUpdate
from app.utils.exceptions import (
    DBEntryNotFoundException,
    DBEntryCreationException,
    DBEntryUpdateException,
    DBEntryDeletionException,
    DatabaseConnectionException,
)

logger = logging.getLogger(__name__)


# pylint: disable=invalid-name
@dataclass
class PodFilter:
    """
    Data class for filtering pod query results.

    Attributes:
        pod_id (int, optional): Filter by pod ID.
        name (str, optional): Filter by pod name.
        namespace (str, optional): Filter by Kubernetes namespace.
        is_elastic (bool, optional): Filter by elastic status.
        assigned_node_id (int, optional): Filter by assigned node ID.
        workload_request_id (int, optional): Filter by workload request ID.
        status (str, optional): Filter by pod status.
    """

    pod_id: UUID = None
    name: str = None
    namespace: str = None
    is_elastic: bool = None
    assigned_node_id: UUID = None
    workload_request_id: UUID = None
    status: str = None


async def create_pod(db: AsyncSession, pod_data: PodCreate):
    """
    Create a new pod entry in the database.

    Args:
        db (AsyncSession): SQLAlchemy async session.
        pod_data (PodCreate): Data for the new pod.

    Returns:
        Pod: The newly created Pod instance.

    Raises:
        DatabaseConnectionException: If the insert fails due to constraints or DB error.
    """
    try:
        logger.debug("Creating pod  with data: %s", pod_data.dict())
        pod = Pod(**pod_data.dict())
        db.add(pod)
        await db.commit()
        await db.refresh(pod)
        logger.debug("Added pod to session")
        return pod
    except SQLAlchemyError as e:
        await db.rollback()
        raise DBEntryCreationException(
            "Failed to create pod", details={"error": str(e)}
        ) from e
    except Exception as e:
        await db.rollback()
        raise DatabaseConnectionException(
            "Unexpected error while creating pod", details={"error": str(e)}
        ) from e


async def get_pod(db: AsyncSession, pfilter: PodFilter):
    """
    Retrieve pods from the database using filters.

    Args:
        db (AsyncSession): SQLAlchemy async session.
        pfilter (PodFilter): Filter conditions.

    Returns:
        List[Pod]: List of pods matching the filter.

    Raises:
        DatabaseConnectionException: On database error or failure.
    """
    try:
        filters = []
        if pfilter.pod_id is not None:
            filters.append(Pod.id == pfilter.pod_id)
        if pfilter.name is not None:
            filters.append(Pod.name == pfilter.name)
        if pfilter.namespace is not None:
            filters.append(Pod.namespace == pfilter.namespace)
        if pfilter.is_elastic is not None:
            filters.append(Pod.is_elastic == pfilter.is_elastic)
        if pfilter.assigned_node_id is not None:
            filters.append(Pod.assigned_node_id == pfilter.assigned_node_id)
        if pfilter.workload_request_id is not None:
            filters.append(Pod.workload_request_id == pfilter.workload_request_id)
        if pfilter.status is not None:
            filters.append(Pod.status == pfilter.status)

        if filters:
            query = select(Pod).where(*filters)
        else:
            query = select(Pod)

        result = await db.execute(query)
        pods = result.scalars().all()
        return pods
    except Exception as e:
        raise DatabaseConnectionException(
            "Unexpected error while retrieving pods", details={"error": str(e)}
        ) from e


async def get_pod_by_id(db: AsyncSession, pod_id: UUID):
    """
    Retrieve a pod by its ID.

    Args:
        db (AsyncSession): The database session.
        pod_id (int): The ID of the pod to retrieve.

    Returns:
        Pod: The pod instance if found.

    Raises:
        DatabaseEntryNotFoundException: If the pod does not exist.
        DatabaseConnectionException: If a database error occurs.
    """
    try:
        result = await db.execute(select(Pod).where(Pod.id == pod_id))
        pod = result.scalar_one_or_none()
        return pod
    except DBEntryNotFoundException:
        raise
    except Exception as e:
        raise DatabaseConnectionException(
            "Unexpected error while retrieving pod", details={"error": str(e)}
        ) from e


async def update_pod(db: AsyncSession, pod_id: UUID, updates: PodUpdate):
    """
    Update an existing pod in the database.

    Args:
        db (AsyncSession): SQLAlchemy async session.
        pod_id (int): ID of the pod to update.
        updates (PodUpdate): Fields to update.

    Returns:
        Pod: The updated pod.

    Raises:
        DatabaseEntryNotFoundException: If the pod does not exist.
        DatabaseConnectionException: On update failure.
    """
    try:
        pod = await get_pod_by_id(db, pod_id)

        for key, value in updates.model_dump(exclude_unset=True).items():
            if not hasattr(pod, key):
                raise AttributeError(f"Pod has no attribute named '{key}'")
            setattr(pod, key, value)

        db.add(pod)
        await db.commit()
        await db.refresh(pod)
        return pod
    except DBEntryNotFoundException:
        raise
    except SQLAlchemyError as e:
        await db.rollback()
        raise DBEntryUpdateException("Failed to update pod",
                                     details={"error": str(e)}) from e
    except Exception as e:
        await db.rollback()
        raise DatabaseConnectionException(
            "Unexpected error while updating pod", details={"error": str(e)}
        ) from e


async def delete_pod(db: AsyncSession, pod_id: UUID):
    """
    Delete a pod by its ID.

    Args:
        db (AsyncSession): SQLAlchemy async session.
        pod_id (int): ID of the pod to delete.

    Returns:
        dict: Success message with deleted pod ID.

    Raises:
        DatabaseEntryNotFoundException: If the pod does not exist.
        DatabaseConnectionException: On delete failure.
    """
    try:
        pod = await get_pod_by_id(db, pod_id)

        await db.delete(pod)
        await db.commit()
        return {"message": f"Pod with ID {pod_id} has been deleted"}
    except DBEntryNotFoundException:
        raise
    except SQLAlchemyError as e:
        await db.rollback()
        raise DBEntryDeletionException(
            "Failed to delete pod", details={"error": str(e)}
        ) from e
    except Exception as e:
        await db.rollback()
        raise DatabaseConnectionException(
            "Unexpected error while deleting pod", details={"error": str(e)}
        ) from e
