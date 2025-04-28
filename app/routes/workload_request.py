from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db, get_async_db
from app import schemas, crud

router = APIRouter(prefix="/workload_request")

# @router.post("/")
# def create(data: schemas.WorkloadRequestCreate, db: Session = Depends(get_db)):
#     return crud.create_workload_request(db, data)


@router.post("/")
async def create(
    data: schemas.WorkloadRequestCreate, db: AsyncSession = Depends(get_async_db)
):
    return await crud.create_workload_request(db, data)


@router.get("/")
async def read_workload_requests(
    name: str = None,
    namespace: str = None,
    api_version: str = None,
    kind: str = None,
    current_scale: int = None,
    db: AsyncSession = Depends(get_async_db),
):
    workloads = await crud.get_workload_requests(
        db,
        name=name,
        namespace=namespace,
        api_version=api_version,
        kind=kind,
        current_scale=current_scale,
    )
    if not workloads:
        return {"error": "No workload requests found"}
    return workloads


@router.put("/{workload_request_id}")
async def update_workload_request(
    workload_request_id: int,
    data: schemas.WorkloadRequestUpdate,
    db: AsyncSession = Depends(get_async_db),
):
    return await crud.update_workload_request(
        db, workload_request_id, updates=data.model_dump(exclude_unset=True)
    )


@router.delete("/{workload_request_id}")
async def delete_workload_request(
    workload_request_id: int,
    db: AsyncSession = Depends(get_async_db),
):
    return await crud.delete_workload_request(db, workload_request_id)
