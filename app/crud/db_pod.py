"""
CRUD operations for managing pods in the database.
This module provides functions to create, read, update, and delete pod records.
It uses SQLAlchemy ORM for database interactions.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Pod
from app.schemas import PodCreate, PodUpdate


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
    pod_id: int = None,
    name: str = None,
    namespace: str = None,
    is_elastic: bool = None,
    assigned_node_id: int = None,
    workload_request_id: int = None,
    status: str = None,
):
    """
    Retrieve pods based on various filters. If no filters are provided, 
    return all pods.
    """
    filters = []
    if pod_id is not None:
        filters.append(Pod.id == pod_id)
    if name is not None:
        filters.append(Pod.name == name)
    if namespace is not None:
        filters.append(Pod.namespace == namespace)
    if is_elastic is not None:
        filters.append(Pod.is_elastic == is_elastic)
    if assigned_node_id is not None:
        filters.append(Pod.assigned_node_id == assigned_node_id)
    if workload_request_id is not None:
        filters.append(Pod.workload_request_id == workload_request_id)
    if status is not None:
        filters.append(Pod.status == status)

    if filters:
        query = select(Pod).where(*filters)
    else:
        query = select(Pod)

    result = await db.execute(query)
    pods = result.scalars().all()
    return pods


async def update_pod(db: AsyncSession, pod_id: int, updates: PodUpdate):
    """
    Update an existing pod.
    """
    result = await db.execute(select(Pod).where(Pod.id == pod_id))
    pod = result.scalar_one_or_none()
    if not pod:
        return None

    for key, value in updates.model_dump(exclude_unset=True).items():
        if hasattr(pod, key):
            setattr(pod, key, value)

    db.add(pod)
    await db.commit()
    await db.refresh(pod)
    return pod


async def delete_pod(db: AsyncSession, pod_id: int):
    """
    Delete a pod by its ID.
    """
    pod = await get_pod(db, pod_id)
    if not pod:
        return {"error": "Pod not found"}

    await db.delete(pod)
    await db.commit()
    return {"message": f"Pod with ID {pod_id} has been deleted"}
