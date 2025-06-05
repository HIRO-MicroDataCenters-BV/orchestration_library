"""
DB pod routes.
This module defines the API endpoints for managing pods in the database.
It includes routes for creating, retrieving, updating, and deleting pod records.
"""


from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_async_db
from app.schemas.pod import PodCreate, PodUpdate
from app.repositories import pod

router = APIRouter(prefix="/db_pod")


# pylint: disable=too-many-arguments,
# This is a filter function, and it can have many parameters.
def pod_filter_from_query(
    pod_id: Optional[UUID] = Query(None),
    name: Optional[str] = Query(None),
    namespace: Optional[str] = Query(None),
    is_elastic: Optional[bool] = Query(None),
    assigned_node_id: Optional[UUID] = Query(None),
    workload_request_id: Optional[UUID] = Query(None),
    status: Optional[str] = Query(None),
):  # pylint: disable=too-many-positional-arguments
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
    return await pod.create_pod(db, data)


@router.get("/")
async def get(
    db: AsyncSession = Depends(get_async_db),
    pod_filter: pod.PodFilter = Depends(pod_filter_from_query),
):
    """
    Retrieve pods based on various filters. If no filters are provided,
    return all pods.
    """

    return await pod.get_pod(db, pod_filter)


@router.get("/{pod_id}")
async def get_by_id(pod_id: UUID, db: AsyncSession = Depends(get_async_db)):
    """
    Retrieve a pod by its ID.
    """
    return await pod.get_pod(db, pod_id)


@router.put("/{pod_id}")
async def update(
    pod_id: UUID, data: PodUpdate, db: AsyncSession = Depends(get_async_db)
):
    """
    Update a pod by its ID.
    """

    return await pod.update_pod(db, pod_id, data)


@router.delete("/{pod_id}")
async def delete(pod_id: UUID, db: AsyncSession = Depends(get_async_db)):
    """
    Delete a pod by its ID.
    """
    return await pod.delete_pod(db, pod_id)
