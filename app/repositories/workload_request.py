"""
CRUD operations for managing workload requests in the database.
"""
from dataclasses import dataclass
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.workload_request import WorkloadRequest
from app.schemas.workload_request import WorkloadRequestCreate


@dataclass
class WorkloadRequestFilter:
    """
    Data class for filtering workload requests.
    This class can be extended with additional filter fields as needed.
    """
    workload_request_id: int = None
    name: str = None
    namespace: str = None
    api_version: str = None
    kind: str = None
    status: str = None
    current_scale: int = None

async def create_workload_request(db: AsyncSession, req: WorkloadRequestCreate):
    """
    Create a new workload request.
    """
    obj = WorkloadRequest(**req.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


async def get_workload_requests(
    db: AsyncSession, wrfilter: WorkloadRequestFilter
):
    """
    Get workload requests based on various optional filters.
    """
    filters = []
    if wrfilter.workload_request_id:
        filters.append(WorkloadRequest.id == wrfilter.workload_request_id)
    if wrfilter.name:
        filters.append(WorkloadRequest.name == wrfilter.name)
    if wrfilter.namespace:
        filters.append(WorkloadRequest.namespace == wrfilter.namespace)
    if wrfilter.api_version:
        filters.append(WorkloadRequest.api_version == wrfilter.api_version)
    if wrfilter.kind:
        filters.append(WorkloadRequest.kind == wrfilter.kind)
    if wrfilter.status:
        filters.append(WorkloadRequest.status == wrfilter.status)
    if wrfilter.current_scale is not None:
        filters.append(WorkloadRequest.current_scale == wrfilter.current_scale)

    query = (
        select(WorkloadRequest).where(*filters) if filters else select(WorkloadRequest)
    )
    result = await db.execute(query)

    workload_requests = result.scalars().all()
    return workload_requests


async def update_workload_request(
    db: AsyncSession, workload_request_id: int, updates: dict
):
    """
    Update a WorkloadRequest based on its ID.
    """
    result = await db.execute(
        select(WorkloadRequest).where(WorkloadRequest.id == workload_request_id)
    )
    workload_request = result.scalar_one_or_none()

    if not workload_request:
        return None

    for key, value in updates.items():
        if hasattr(workload_request, key):
            setattr(workload_request, key, value)

    db.add(workload_request)
    await db.commit()
    await db.refresh(workload_request)

    return workload_request


async def delete_workload_request(db: AsyncSession, workload_request_id: int):
    """
    Delete a WorkloadRequest by its ID.
    """
    result = await db.execute(
        select(WorkloadRequest).where(WorkloadRequest.id == workload_request_id)
    )
    workload_request = result.scalar_one_or_none()

    if not workload_request:
        return {"error": "WorkloadRequest not found"}

    await db.delete(workload_request)
    await db.commit()

    return {
        "message": f"WorkloadRequest with ID {workload_request_id} has been deleted"
    }
