"""
DB pod decision routes.
This module defines the API endpoints for managing nodes in the database.
It includes routes for creating, retrieving, updating, and deleting nodes.
"""

import time
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_async_db
from app.repositories.workload_timing import (
    create_workload_timing,
    get_all_workload_timings,
    get_workload_timings,
    update_workload_timing,
)
from app.schemas.workload_timing_schema import (
    WorkloadTimingSchema,
    WorkloadTimingCreate,
    WorkloadTimingUpdate,
)

router = APIRouter(prefix="/workload_timing", tags=["Workload Timing"])


@router.post(path="/", response_model=WorkloadTimingSchema)
async def create_workload_timing_route(
    data: WorkloadTimingCreate,
    db_session: AsyncSession = Depends(get_async_db),
):
    """
    Create a new WorkloadRequestDecision entry.

    Args:
        data (WorkloadRequestDecisionSchema): The pod decision data to create.
        db_session (AsyncSession): Database session dependency.

    Returns:
        WorkloadRequestDecisionSchema: The newly created pod decision.
    """
    metrics_details = {
        "start_time": time.time(),
        "method": "POST",
        "endpoint": "/workload_timing",
    }
    return await create_workload_timing(
        db_session, data, metrics_details=metrics_details
    )


@router.get("/", response_model=list[WorkloadTimingSchema])
async def list_or_filter_workload_timings(
    pod_name: str | None = Query(default=None),
    namespace: str | None = Query(default=None),
    skip: int = 0,
    limit: int = 100,
    db_session: AsyncSession = Depends(get_async_db),
):
    """
    If pod_name & namespace provided -> filter; else return paginated list.
    """
    if pod_name and namespace:
        return await get_workload_timings(db_session, pod_name, namespace)
    return await get_all_workload_timings(db_session, skip=skip, limit=limit)


# @router.get("/", response_model=list[WorkloadTimingSchema])
# async def get_all_workload_timings_route(
#     db_session: AsyncSession = Depends(get_async_db),
#     skip: int = Query(0, ge=0),
#     limit: int = Query(100, gt=0, le=1000),
# ):
#     """
#     Retrieve all WorkloadTimings with pagination.

#     Args:
#         db_session (AsyncSession): Database session dependency.
#         skip (int): Number of records to skip for pagination.
#         limit (int): Maximum number of records to return.

#     Returns:
#         List[WorkloadTimingSchema]: List of workload timings.
#     """
#     metrics_details = {
#         "start_time": time.time(),
#         "method": "GET",
#         "endpoint": "/workload_timing",
#     }
#     return await get_all_workload_timings(
#         db_session, skip, limit, metrics_details=metrics_details
#     )

# @router.get("/", response_model=WorkloadTimingSchema)
# async def get_workload_timings_route(
#     pod_name: str,
#     namespace: str,
#     db_session: AsyncSession = Depends(get_async_db)
# ):
#     """
#     Retrieve all WorkloadTimings for a specific pod and namespace.

#     Args:
#         db_session (AsyncSession): Database session dependency.
#         pod_name (str): Name of the pod.
#         namespace (str): Namespace of the pod.

#     Returns:
#         WorkloadTimingSchema: Entry of workload timings.
#     """
#     metrics_details = {
#         "start_time": time.time(),
#         "method": "GET",
#         "endpoint": "/workload_timing",
#     }
#     return await get_workload_timings(
#         db_session, pod_name, namespace, metrics_details=metrics_details
#     )

@router.patch("/{workload_timing_id}", response_model=WorkloadTimingSchema)
async def update_workload_timing_route(
    workload_timing_id: str,
    data: WorkloadTimingUpdate,
    db_session: AsyncSession = Depends(get_async_db),
):
    """
    Update an existing WorkloadTiming entry.

    Args:
        workload_timing_id (str): The ID of the workload timing to update.
        data (WorkloadTimingCreate): The updated workload timing data.
        db_session (AsyncSession): Database session dependency.

    Returns:
        WorkloadTimingSchema: The updated workload timing.
    """
    metrics_details = {
        "start_time": time.time(),
        "method": "PATCH",
        "endpoint": f"/workload_timing/{workload_timing_id}",
    }
    return await update_workload_timing(
        db_session, workload_timing_id, data, metrics_details=metrics_details
    )