"""
Routes for managing workload request decisions.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import workload_request_decision as wrd
from app.database import get_async_db
from app import schemas

router = APIRouter(prefix="/workload_request_decision")

# @router.post("/")
# def create(data: schemas.WorkloadRequestDecisionCreate, db: Session = Depends(get_db)):
#     return crud.create_workload_request_decision(db, data)


@router.post("/")
async def create(
    data: schemas.WorkloadRequestDecisionCreate,
    db: AsyncSession = Depends(get_async_db),
):
    """
    Create a new workload request decision.
    """
    return await wrd.create_workload_request_decision(db, data)


@router.get("/")
async def read(
    workload_request_id: int = None,
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
        workload_request_id=workload_request_id,
        node_name=node_name,
        queue_name=queue_name,
        status=status,
    )
    if not decisions:
        return {"error": "No decisions found"}
    return decisions


@router.get("/{workload_request_id}")
async def read_by_id(workload_request_id: int, db: AsyncSession = Depends(get_async_db)):
    """
    Retrieve a workload request decision by its ID.
    """
    decision = await wrd.get_workload_request_decision(
        db, workload_request_id=workload_request_id
    )
    if not decision:
        return {"error": "Decision not found"}
    return decision


@router.put("/{workload_request_id}")
async def update(
    workload_request_id: int,
    data: schemas.WorkloadRequestDecisionUpdate,
    db: AsyncSession = Depends(get_async_db),
):
    """
    Update a workload request decision by its ID.
    """
    return await wrd.update_workload_request_decision(db, workload_request_id, data)


@router.delete("/{workload_request_id}")
async def delete(workload_request_id: int, db: AsyncSession = Depends(get_async_db)):
    """
    Delete a workload request decision by its ID.
    """
    return await wrd.delete_workload_request_decision(
        db, workload_request_id=workload_request_id
    )
