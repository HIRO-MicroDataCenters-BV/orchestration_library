"""
Workload Action API routes

This module defines the API endpoints for managing workload actions in the database.
It includes routes for creating, retrieving, updating, and deleting workload actions.
"""

import time
from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_async_db
from app.schemas.workload_action_schema import (
    WorkloadActionCreate,
    WorkloadActionFilters,
    WorkloadActionUpdate,
    WorkloadAction,
)
from app.repositories.workload_action import (
    create_workload_action,
    get_workload_action_by_id,
    list_workload_actions,
    update_workload_action,
    delete_workload_action,
)

router = APIRouter(prefix="/workload_action", tags=["Workload Action"])


@router.post("/", response_model=WorkloadAction)
async def create_workload_action_route(
    data: WorkloadActionCreate, db_session: AsyncSession = Depends(get_async_db)
):
    """
    Create a new workload action entry.

    Args:
        data (WorkloadActionCreate): The workload action data to create.
        db_session (AsyncSession): Database session dependency.

    Returns:
        WorkloadAction: The newly created workload action.
    """
    metrics_details  = {
        "start_time": time.time(),
        "method": "POST",
        "endpoint": "/workload_action"
    }
    return await create_workload_action(db_session, data, metrics_details=metrics_details)


@router.get("/{action_id}", response_model=WorkloadAction)
async def get_workload_action_route(
    action_id: UUID, db_session: AsyncSession = Depends(get_async_db)
):
    """
    Retrieve a single workload action by ID.

    Args:
        action_id (UUID): The ID of the workload action to retrieve.
        db_session (AsyncSession): Database session dependency.

    Returns:
        WorkloadAction: The workload action with the given ID.
    """
    metrics_details = {
        "start_time": time.time(),
        "method": "GET",
        "endpoint": f"/workload_action/{action_id}"
    }
    return await get_workload_action_by_id(db_session, action_id, metrics_details=metrics_details)


@router.get("/", response_model=list[WorkloadAction])
async def get_all_workload_actions_route(
    db_session: AsyncSession = Depends(get_async_db),
    filters: WorkloadActionFilters = Depends(),
):
    """
    Retrieve all workload actions with optional filters.

    Args:
        db_session (AsyncSession): Database session dependency.
        filters (WorkloadActionFilters): Filters to apply to the workload actions.

    Returns:
        list[WorkloadAction]: List of workload actions matching the filters.
    """
    metrics_details = {
        "start_time": time.time(),
        "method": "GET",
        "endpoint": "/workload_action"
    }
    return await list_workload_actions(
        db_session, filters=filters.model_dump(exclude_none=True), metrics_details=metrics_details
    )


@router.put("/{action_id}", response_model=WorkloadAction)
async def update_workload_action_route(
    action_id: UUID,
    data: WorkloadActionUpdate,
    db_session: AsyncSession = Depends(get_async_db),
):
    """
    Update an existing workload action.

    Args:
        action_id (UUID): The ID of the workload action to update.
        data (WorkloadActionUpdate): The updated workload action data.
        db_session (AsyncSession): Database session dependency.

    Returns:
        WorkloadAction: The updated workload action.
    """
    metrics_details = {
        "start_time": time.time(),
        "method": "PUT",
        "endpoint": f"/workload_action/{action_id}"
    }
    return await update_workload_action(db_session, action_id, data, metrics_details=metrics_details)


@router.delete("/{action_id}", response_model=None)
async def delete_workload_action_route(
    action_id: UUID, db_session: AsyncSession = Depends(get_async_db)
):
    """
    Delete a workload action by ID.

    Args:
        action_id (UUID): The ID of the workload action to delete.
        db_session (AsyncSession): Database session dependency.

    Returns:
        None
    """
    metrics_details = {
        "start_time": time.time(),
        "method": "DELETE",
        "endpoint": f"/workload_action/{action_id}"
    }
    return await delete_workload_action(db_session, action_id, metrics_details=metrics_details)
