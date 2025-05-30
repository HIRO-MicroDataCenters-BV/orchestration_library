"""
DB pod routes.
This module defines the API endpoints for managing pods in the database.
It includes routes for creating, retrieving, updating, and deleting pod records.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_async_db
from app.schemas.pod import PodFilterQuery
from app.schemas.pod import PodCreate, PodUpdate
from app.repositories import pod
from app.utils.exceptions import DatabaseConnectionException

router = APIRouter(prefix="/db_pod")

# pylint: disable=too-many-arguments, disable=invalid-name
"""# pylint: disable=too-many-positional-arguments"""


def pod_filter_from_query(filter_query: PodFilterQuery):
    """
    Create a PodFilter object from query parameters.
    This function is used to filter pods based on various criteria.
    """

    filter_dict = filter_query.dict(exclude_none=True)
    return pod.PodFilter(**filter_dict)


@router.post("/")
async def create(data: PodCreate, db: AsyncSession = Depends(get_async_db)):
    """
    Create a new pod.
    """
    try:
        return await pod.create_pod(db, data)
    except SQLAlchemyError as e:
        raise DatabaseConnectionException(
            "Failed to create pod", details={"error": str(e)}
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
async def get_by_id(pod_id: int, db: AsyncSession = Depends(get_async_db)):
    """
    Retrieve a pod by its ID.
    """
    try:
        return await pod.get_pod(db, pod_id)
    except SQLAlchemyError as e:
        raise DatabaseConnectionException(
            f"Failed to retrieve pod with ID {pod_id}", details={"error": str(e)}
        ) from e


@router.put("/{pod_id}")
async def update(
    pod_id: int, data: PodUpdate, db: AsyncSession = Depends(get_async_db)
):
    """
    Update a pod by its ID.
    """
    try:
        return await pod.update_pod(db, pod_id, data)
    except SQLAlchemyError as e:
        raise DatabaseConnectionException(
            f"Failed to update pod with ID {pod_id}", details={"error": str(e)}
        ) from e


@router.delete("/{pod_id}")
async def delete(pod_id: int, db: AsyncSession = Depends(get_async_db)):
    """
    Delete a pod by its ID.
    """
    try:
        return await pod.delete_pod(db, pod_id)
    except SQLAlchemyError as e:
        raise DatabaseConnectionException(
            f"Failed to delete pod with ID {pod_id}", details={"error": str(e)}
        ) from e
