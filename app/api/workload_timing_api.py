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
)
from app.schemas.workload_timing_schema import (
    WorkloadTimingSchema,
    WorkloadTimingCreate,
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
async def get_all_workload_timings_route(
    db_session: AsyncSession = Depends(get_async_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, gt=0, le=1000),
):
    """
    Retrieve all WorkloadTimings with pagination.

    Args:
        db_session (AsyncSession): Database session dependency.
        skip (int): Number of records to skip for pagination.
        limit (int): Maximum number of records to return.

    Returns:
        List[WorkloadRequestDecisionSchema]: List of pod decisions.
    """
    metrics_details = {
        "start_time": time.time(),
        "method": "GET",
        "endpoint": "/workload_timing",
    }
    return await get_all_workload_timings(
        db_session, skip, limit, metrics_details=metrics_details
    )
