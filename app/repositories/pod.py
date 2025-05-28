"""
CRUD operations for managing pods in the database.
This module provides functions to create, read, update, and delete pod records.
It uses SQLAlchemy ORM for database interactions.
"""
from dataclasses import dataclass
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.pod import Pod
from app.schemas.pod import PodCreate, PodUpdate


@dataclass
class PodFilter:
    """
    Data class for filtering pods.
    This class can be extended with additional filter fields as needed.
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
    Create a new pod.
    """
    pod = Pod(**pod_data.model_dump())
    db.add(pod)
    await db.commit()
    await db.refresh(pod)
    return pod


async def get_pod(
    db: AsyncSession,
    pfilter: PodFilter
):
    """
    Retrieve pods based on various filters. If no filters are provided, 
    return all pods.
    """
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


async def get_pod_by_id(db: AsyncSession, pod_id: UUID):
    """
    Retrieve a pod by its ID.
    """
    result = await db.execute(select(Pod).where(Pod.id == pod_id))
    pod = result.scalar_one_or_none()
    return pod


async def update_pod(db: AsyncSession, pod_id: UUID, updates: PodUpdate):
    """
    Update an existing pod.
    """
    pod = await get_pod_by_id(db, pod_id)
    if not pod:
        return None

    for key, value in updates.model_dump(exclude_unset=True).items():
        if hasattr(pod, key):
            setattr(pod, key, value)

    db.add(pod)
    await db.commit()
    await db.refresh(pod)
    return pod


async def delete_pod(db: AsyncSession, pod_id: UUID):
    """
    Delete a pod by its ID.
    """
    pod = await get_pod_by_id(db, pod_id)
    if not pod:
        return {"error": "Pod not found"}

    await db.delete(pod)
    await db.commit()
    return {"message": f"Pod with ID {pod_id} has been deleted"}
