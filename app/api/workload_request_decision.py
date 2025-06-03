"""
Routes for managing workload request decisions.
"""

from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import workload_request_decision as wrd
from app.db.database import get_async_db
from app.schemas.workload_request_decision import (
    WorkloadRequestDecisionCreate,
    WorkloadRequestDecisionUpdate,
)

router = APIRouter(prefix="/workload_request_decision")


# pylint: disable=invalid-name
@router.post("/")
async def create(
    data: WorkloadRequestDecisionCreate,
    db: AsyncSession = Depends(get_async_db),
):
    """
    Create a new workload request decision.
    """
    return await wrd.create_workload_request_decision(db, data)


@router.get("/")
async def read(
    pod_id: UUID = None,
    node_name: str = None,
    queue_name: str = None,
    status: str = None,
    db: AsyncSession = Depends(get_async_db),
):
    """
    Retrieve workload request decisions based on various filters.
    If no filters are provided, return all decisions.
    """
    decisions = await wrd.get_workload_request_decision(
        db,
        pod_id=pod_id,
        node_name=node_name,
        queue_name=queue_name,
        status=status,
    )
    if not decisions:
        return {"error": "No decisions found"}
    return decisions


@router.get("/{pod_id}")
async def read_by_id(pod_id: UUID, db: AsyncSession = Depends(get_async_db)):
    """
    Retrieve a workload request decision by its ID.
    """
    decision = await wrd.get_workload_request_decision(db, pod_id=pod_id)
    if not decision:
        return {"error": "Decision not found"}
    return decision


@router.put("/{pod_id}")
async def update(
    pod_id: UUID,
    data: WorkloadRequestDecisionUpdate,
    db: AsyncSession = Depends(get_async_db),
):
    """
    Update a workload request decision by its ID.
    """
    return await wrd.update_workload_request_decision(db, pod_id, data)


@router.delete("/{pod_id}")
async def delete(pod_id: UUID, db: AsyncSession = Depends(get_async_db)):
    """
    Delete a workload request decision by its ID.
    """
    return await wrd.delete_workload_request_decision(db, pod_id=pod_id)
