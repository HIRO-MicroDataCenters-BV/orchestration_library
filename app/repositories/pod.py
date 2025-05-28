"""
CRUD operations for managing pods in the database.
This module provides functions to create, read, update, and delete pod records.
It uses SQLAlchemy ORM for database interactions.
"""
from dataclasses import dataclass
import logging
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.pod import Pod
from app.schemas.pod import PodCreate, PodUpdate
from app.utils.exceptions import (
    DatabaseConnectionException,
    DatabaseEntryNotFoundException,
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

    pod_id: int = None
    name: str = None
    namespace: str = None
    is_elastic: bool = None
    assigned_node_id: int = None
    workload_request_id: int = None
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
    except IntegrityError as e:
        logger.error("Integrity error while creating pod: %s", str(e))
        await db.rollback()
        raise DatabaseConnectionException(
            "Invalid pod data", details={"error": str(e)}
        ) from e
    except SQLAlchemyError as e:
        logger.error("Database error while creating pod: %s", str(e))
        await db.rollback()
        raise DatabaseConnectionException(
            "Failed to create  pod", details={"error": str(e)}
        ) from e
    except Exception as e:
        logger.error("Unexpected error while creating  pod: %s", str(e))
        await db.rollback()
        raise DatabaseConnectionException(
            "An unexpected error occurred while creating pod", details={"error": str(e)}
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
    except SQLAlchemyError as e:
        logger.error("Database error while retrieving pods: %s", str(e))
        raise DatabaseConnectionException(
            "Failed to retrieve pods", details={"error": str(e)}
        ) from e
    except Exception as e:
        logger.error("Unexpected error while retrieving pods: %s", str(e))
        raise DatabaseConnectionException(
            "An unexpected error occurred while retrieving pods",
            details={"error": str(e)},
        ) from e


async def get_pod_by_id(db: AsyncSession, pod_id: int):
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
        if not isinstance(pod_id, int):
            raise ValueError(f"Expected pod_id to be int, got {type(pod_id).__name__}")
        result = await db.execute(select(Pod).where(Pod.id == pod_id))
        pod = result.scalar_one_or_none()
        if not pod:
            raise DatabaseEntryNotFoundException()
        return pod
    except SQLAlchemyError as e:
        logger.error("Database error while retrieving pod by ID: %s", str(e))
        raise DatabaseConnectionException(
            "Failed to retrieve pod by ID", details={"error": str(e)}
        ) from e
    except Exception as e:
        logger.error("Unexpected error while retrieving pod by ID: %s", str(e))
        raise DatabaseConnectionException(
            "An unexpected error occurred while retrieving pod by ID",
            details={"error": str(e)},
        ) from e


async def update_pod(db: AsyncSession, pod_id: int, updates: PodUpdate):
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
        if not isinstance(pod_id, int):
            raise ValueError(f"Expected pod_id to be int, got {type(pod_id).__name__}")
        pod = await get_pod_by_id(db, pod_id)
        if not pod:
            raise DatabaseEntryNotFoundException()

        for key, value in updates.model_dump(exclude_unset=True).items():
            if not hasattr(pod, key):
                raise AttributeError(f"Pod has no attribute named '{key}'")
            setattr(pod, key, value)

        db.add(pod)
        await db.commit()
        await db.refresh(pod)
        return pod
    except SQLAlchemyError as e:
        logger.error("Database error while updating pod: %s", str(e))
        await db.rollback()
        raise DatabaseConnectionException(
            "Failed to update pod", details={"error": str(e)}
        ) from e
    except Exception as e:
        logger.error("Unexpected error while updating pod: %s", str(e))
        await db.rollback()
        raise DatabaseConnectionException(
            "An unexpected error occurred while updating pod", details={"error": str(e)}
        ) from e


async def delete_pod(db: AsyncSession, pod_id: int):
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
        if not isinstance(pod_id, int):
            raise ValueError(f"Expected pod_id to be int, got {type(pod_id).__name__}")
        pod = await get_pod_by_id(db, pod_id)
        if not pod:
            raise DatabaseEntryNotFoundException()
        await db.delete(pod)
        await db.commit()
        return {"message": f"Pod with ID {pod_id} has been deleted"}
    except SQLAlchemyError as e:
        logger.error("Database error while deleting pod: %s", str(e))
        await db.rollback()
        raise DatabaseConnectionException(
            "Failed to delete pod", details={"error": str(e)}
        ) from e
    except Exception as e:
        logger.error("Unexpected error while deleting pod: %s", str(e))
        await db.rollback()
        raise DatabaseConnectionException(
            "An unexpected error occurred while deleting pod", details={"error": str(e)}
        ) from e
