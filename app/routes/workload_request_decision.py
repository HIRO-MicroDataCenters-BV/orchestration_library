from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db, get_async_db
from sqlalchemy.ext.asyncio import AsyncSession
from app import schemas, crud

router = APIRouter(prefix="/workload_request_decision")

# @router.post("/")
# def create(data: schemas.WorkloadRequestDecisionCreate, db: Session = Depends(get_db)):
#     return crud.create_workload_request_decision(db, data)


@router.post("/")
async def create(
    data: schemas.WorkloadRequestDecisionCreate,
    db: AsyncSession = Depends(get_async_db),
):
    return await crud.create_workload_request_decision(db, data)


@router.get("/")
async def read(
    workload_request_id: int = None,
    node_name: str = None,
    queue_name: str = None,
    status: str = None,
    db: AsyncSession = Depends(get_async_db),
):
    decisions = await crud.get_workload_request_decision(
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
async def read(workload_request_id: int, db: AsyncSession = Depends(get_async_db)):
    decision = await crud.get_workload_request_decision(
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
    return await crud.update_workload_request_decision(db, workload_request_id, data)


@router.delete("/{workload_request_id}")
async def delete(workload_request_id: int, db: AsyncSession = Depends(get_async_db)):
    return await crud.delete_workload_request_decision(
        db, workload_request_id=workload_request_id
    )
