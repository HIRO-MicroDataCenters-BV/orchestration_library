"""
Routes for managing workload request
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_async_db
from app.schemas.workload_request import WorkloadRequestCreate, WorkloadRequestUpdate
from app.repositories import workload_request as wr


router = APIRouter(prefix="/workload_request")


@router.post("/")
async def create(
    data: WorkloadRequestCreate, db: AsyncSession = Depends(get_async_db)
):
    """
    Create a new workload request.
    """
    return await wr.create_workload_request(db, data)


@router.get("/")
async def read_workload_requests(
    name: str = None,
    namespace: str = None,
    api_version: str = None,
    kind: str = None,
    current_scale: int = None,
    db: AsyncSession = Depends(get_async_db),
):
    """
    Retrieve workload requests based on various filters.
    If no filters are provided, return all workload requests.
    """
    workloads = await wr.get_workload_requests(
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
    data: WorkloadRequestUpdate,
    db: AsyncSession = Depends(get_async_db),
):
    """
    Update a workload request by its ID.
    """
    return await wr.update_workload_request(
        db, workload_request_id, updates=data.model_dump(exclude_unset=True)
    )


@router.delete("/{workload_request_id}")
async def delete_workload_request(
    workload_request_id: int,
    db: AsyncSession = Depends(get_async_db),
):
    """
    Delete a workload request by its ID.
    """
    return await wr.delete_workload_request(db, workload_request_id)


@router.get("/{workload_request_id}")
async def read_workload_request_by_id(
    workload_request_id: int, db: AsyncSession = Depends(get_async_db)
):
    """
    Retrieve a workload request by its ID.
    """
    requested_id = await wr.get_workload_requests(
        db, workload_request_id=workload_request_id
    )
    if not requested_id:
        return {"error": "ID not found"}
    return requested_id
