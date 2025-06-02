"""
DB pod routes.
This module defines the API endpoints for managing pods in the database.
It includes routes for creating, retrieving, updating, and deleting pod records.
"""


from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_async_db
from app.schemas.pod import PodCreate, PodUpdate
from app.repositories import pod
from app.utils.exceptions import (
    DatabaseConnectionException,
    DBEntryNotFoundException,
    DBEntryCreationException,
    DBEntryUpdateException,
    DBEntryDeletionException,
)

router = APIRouter(prefix="/db_pod")


# pylint: disable=too-many-arguments, disable=invalid-name
# This is a filter function, and it can have many parameters.
def pod_filter_from_query(
    pod_id: Optional[UUID] = Query(None),
    name: Optional[str] = Query(None),
    namespace: Optional[str] = Query(None),
    is_elastic: Optional[bool] = Query(None),
    assigned_node_id: Optional[UUID] = Query(None),
    workload_request_id: Optional[UUID] = Query(None),
    status: Optional[str] = Query(None),
):  # pylint: too-many-positional-arguments
    """
    Create a PodFilter object from query parameters.
    This function is used to filter pods based on various criteria.
    """
    return pod.PodFilter(
        pod_id=pod_id,
        name=name,
        namespace=namespace,
        is_elastic=is_elastic,
        assigned_node_id=assigned_node_id,
        workload_request_id=workload_request_id,
        status=status,
    )


@router.post("/")
async def create(data: PodCreate, db: AsyncSession = Depends(get_async_db)):
    """
    Create a new pod.
    """

    try:
        return await pod.create_pod(db, data)
    except SQLAlchemyError as e:
        raise DBEntryCreationException(
            "Failed to create pod", details={"error": str(e)}
        ) from e
    except Exception as e:
        raise DatabaseConnectionException(
            "Unexpected error during pod creation", details={"error": str(e)}
        ) from e


@router.get("/")
async def get(
    db: AsyncSession = Depends(get_async_db),
    pod_filter: pod.PodFilter = Depends(pod_filter_from_query),
):
    """
    Retrieve pods based on various filters. If no filters are provided,
    return all pods.
    """
    try:
        return await pod.get_pod(db, pod_filter)
    except SQLAlchemyError as e:
        raise DatabaseConnectionException(
            "Failed to retrieve pods", details={"error": str(e)}
        ) from e


@router.get("/{pod_id}")
async def get_by_id(pod_id: UUID, db: AsyncSession = Depends(get_async_db)):
    """
    Retrieve a pod by its ID.
    """

    try:
        result = await pod.get_pod(db, pod_id)
        if not result:
            raise DBEntryNotFoundException(
                f"Pod with ID {pod_id} not found", details={"pod_id": str(pod_id)}
            )
        return result
    except SQLAlchemyError as e:
        raise DatabaseConnectionException(
            f"Failed to update pod with ID {pod_id}", details={"error": str(e)}
        ) from e


@router.put("/{pod_id}")
async def update(
    pod_id: UUID, data: PodUpdate, db: AsyncSession = Depends(get_async_db)
):
    """
    Update a pod by its ID.
    """
    try:
        result = await pod.update_pod(db, pod_id, data)
        if not result:
            raise DBEntryUpdateException(
                f"Pod with ID {pod_id} not found or update failed",
                details={"pod_id": str(pod_id)},
            )

        return result
    except SQLAlchemyError as e:
        raise DatabaseConnectionException(
            f"Failed to update pod with ID {pod_id}", details={"error": str(e)}
        ) from e


@router.delete("/{pod_id}")
async def delete(pod_id: UUID, db: AsyncSession = Depends(get_async_db)):
    """
    Delete a pod by its ID.
    """
    try:
        result = await pod.delete_pod(db, pod_id)
        if "error" in result:
            raise DBEntryDeletionException(
                f"Pod with ID {pod_id} not found or deletion failed",
                details={"pod_id": str(pod_id)},
            )
        return result
    except SQLAlchemyError as e:
        raise DatabaseConnectionException(
            f"Failed to delete pod with ID {pod_id}", details={"error": str(e)}
        ) from e
