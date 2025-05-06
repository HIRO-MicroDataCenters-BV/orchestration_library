from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import WorkloadRequest
from app.schemas import WorkloadRequestCreate


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
    db: AsyncSession,
    workload_request_id: int = None,
    name: str = None,
    namespace: str = None,
    api_version: str = None,
    kind: str = None,
    current_scale: int = None,
):
    """
    Get workload requests based on various optional filters.
    """
    filters = []
    if workload_request_id:
        filters.append(WorkloadRequest.id == workload_request_id)
    if name:
        filters.append(WorkloadRequest.name == name)
    if namespace:
        filters.append(WorkloadRequest.namespace == namespace)
    if api_version:
        filters.append(WorkloadRequest.api_version == api_version)
    if kind:
        filters.append(WorkloadRequest.kind == kind)
    if current_scale is not None:
        filters.append(WorkloadRequest.current_scale == current_scale)

    # Log the filters being applied
    print(f"Filters applied: {filters}")

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
