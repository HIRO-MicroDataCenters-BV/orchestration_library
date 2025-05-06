from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import WorkloadRequestPod
from app.schemas import WorkloadRequestPodCreate, WorkloadRequestPodUpdate


async def create_workload_request_pod(db: AsyncSession, req: WorkloadRequestPodCreate):
    """
    Create a new workload request.
    """
    obj = WorkloadRequestPod(**req.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


async def get_workload_request_pods(
    db: AsyncSession,
    workload_request_pod_id: int = None,
    workload_request_id: int = None,
    pod_id: int = None,
):
    """
    Retrieve WorkloadRequestPod entries based on optional filters.
    """
    filters = []
    if workload_request_pod_id:
        filters.append(WorkloadRequestPod.id == workload_request_pod_id)
    if workload_request_id:
        filters.append(WorkloadRequestPod.workload_request_id == workload_request_id)
    if pod_id:
        filters.append(WorkloadRequestPod.pod_id == pod_id)

    query = (
        select(WorkloadRequestPod).where(*filters)
        if filters
        else select(WorkloadRequestPod)
    )
    result = await db.execute(query)
    return result.scalars().all()


async def delete_workload_request_pod(db: AsyncSession, workload_request_pod_id: int):
    """
    Delete a WorkloadRequestPod by ID.
    """
    result = await db.execute(
        select(WorkloadRequestPod).where(
            WorkloadRequestPod.id == workload_request_pod_id
        )
    )
    entry = result.scalar_one_or_none()

    if not entry:
        return {"error": "WorkloadRequestPod not found"}

    await db.delete(entry)
    await db.commit()

    return {
        "message": f"WorkloadRequestPod with ID {workload_request_pod_id} has been deleted"
    }


async def update_workload_request_pod(
    db: AsyncSession, workload_request_pod_id: int, updates: dict
):
    """
    Update a WorkloadRequestPod based on its ID.
    """
    # Fetch the WorkloadRequestPod object by ID
    result = await db.execute(
        select(WorkloadRequestPod).where(
            WorkloadRequestPod.id == workload_request_pod_id
        )
    )
    workload_request_pod = result.scalar_one_or_none()

    if not workload_request_pod:
        return {"error": "WorkloadRequestPod not found"}

    # Apply updates to the object
    for key, value in updates.items():
        if hasattr(workload_request_pod, key):
            setattr(workload_request_pod, key, value)

    # Add the updated object to the session and commit changes
    db.add(workload_request_pod)
    await db.commit()
    await db.refresh(workload_request_pod)

    return workload_request_pod
