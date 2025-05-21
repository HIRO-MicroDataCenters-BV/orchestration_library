"""
CRUD operations for managing workload request decission in the database.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.workload_request_decision import WorkloadRequestDecision
from app.schemas.workload_request_decision import WorkloadRequestDecisionCreate


async def create_workload_request_decision(
    db: AsyncSession, decision: WorkloadRequestDecisionCreate
):
    """
    Create a new workload request decision.
    """
    obj = WorkloadRequestDecision(**decision.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


async def update_workload_request_decision(
    db: AsyncSession, workload_request_id: int, updates: dict
):
    """
    Update a workload request decision by its workload_request_id.
    """
    result = await db.execute(
        select(WorkloadRequestDecision).where(
            WorkloadRequestDecision.workload_request_id == workload_request_id
        )
    )
    decision = result.scalar_one_or_none()
    if not decision:
        return None

    for key, value in updates.items():
        if hasattr(decision, key):
            setattr(decision, key, value)

    db.add(decision)
    await db.commit()
    await db.refresh(decision)
    return decision


async def get_workload_request_decision(
    db: AsyncSession,
    workload_request_id: int = None,
    node_name: str = None,
    queue_name: str = None,
    status: str = None,
):
    """
    Get workload request decisions based on various filters.
    """
    filters = []
    if workload_request_id:
        filters.append(
            WorkloadRequestDecision.workload_request_id == workload_request_id
        )
    if node_name:
        filters.append(WorkloadRequestDecision.node_name == node_name)
    if queue_name:
        filters.append(WorkloadRequestDecision.queue_name == queue_name)
    if status:
        filters.append(WorkloadRequestDecision.status == status)
    if filters:
        query = select(WorkloadRequestDecision).where(*filters)
    else:
        query = select(WorkloadRequestDecision)

    result = await db.execute(query)
    decision = result.scalars().all()
    return decision


async def delete_workload_request_decision(db: AsyncSession, workload_request_id: int):
    """
    Delete a workload request decision by its workload_request_id.
    """
    decision = await get_workload_request_decision(
        db, workload_request_id=workload_request_id
    )
    print(f"Decision: {decision}")
    if not decision:
        return {"error": "Decision not found"}

    if isinstance(decision, list):
        for dec in decision:
            await db.delete(dec)
    else:
        await db.delete(decision)
    await db.commit()
    return {"message": f"Decision with ID {workload_request_id} has been deleted"}
