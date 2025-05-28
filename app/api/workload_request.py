"""
Routes for managing workload request
"""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_async_db
from app.schemas.workload_request import WorkloadRequestCreate, WorkloadRequestUpdate
from app.repositories import workload_request as wr


router = APIRouter(prefix="/workload_request")

# pylint: disable=too-many-arguments,too-many-positional-arguments
# This is a filter function, and it can have many parameters.
def workload_request_filter_from_query(
    workload_request_id:  Optional[UUID] = Query(None),
    name: Optional[str] = Query(None),
    namespace: Optional[str] = Query(None),
    api_version: Optional[str] = Query(None),
    kind: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    current_scale: Optional[int] = Query(None)
):
    """
    Create a WorkloadRequestFilter object from query parameters.
    This function is used to filter workload requests based on various criteria.
    """
    return wr.WorkloadRequestFilter(
        workload_request_id=workload_request_id,
        name=name,
        namespace=namespace,
        api_version=api_version,
        kind=kind,
        status=status,
        current_scale=current_scale,
    )

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
    db: AsyncSession = Depends(get_async_db),
    workload_request_filter: wr.WorkloadRequestFilter = Depends(workload_request_filter_from_query)
):
    """
    Retrieve workload requests based on various filters.
    If no filters are provided, return all workload requests.
    """
    workloads = await wr.get_workload_requests(
        db, workload_request_filter
    )
    if not workloads:
        return {"error": "No workload requests found"}
    return workloads


@router.put("/{workload_request_id}")
async def update_workload_request(
    workload_request_id: UUID,
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
    workload_request_id: UUID,
    db: AsyncSession = Depends(get_async_db),
):
    """
    Delete a workload request by its ID.
    """
    return await wr.delete_workload_request(db, workload_request_id)


@router.get("/{workload_request_id}")
async def read_workload_request_by_id(
    workload_request_id: UUID, db: AsyncSession = Depends(get_async_db)
):
    """
    Retrieve a workload request by its ID.
    """
    requested_id = await wr.get_workload_requests(
        db, wr.WorkloadRequestFilter(workload_request_id=workload_request_id)
    )
    if not requested_id:
        return {"error": "ID not found"}
    return requested_id
