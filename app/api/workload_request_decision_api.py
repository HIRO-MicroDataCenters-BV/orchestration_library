"""
DB pod decision routes.
This module defines the API endpoints for managing nodes in the database.
It includes routes for creating, retrieving, updating, and deleting nodes.
"""
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_async_db
from app.schemas.workload_request_decision_schema import (
    WorkloadRequestDecisionUpdate,
    WorkloadRequestDecisionSchema,
    WorkloadRequestDecisionCreate
)
from app.repositories.workload_request_decision import (
    create_workload_decision,
    get_all_workload_decisions,
    get_workload_decision,
    update_workload_decision,
    delete_workload_decision
)

router = APIRouter(prefix="/workload_request_decision", tags=["Workload Request Decision"])


@router.post(path="/", response_model=WorkloadRequestDecisionSchema)
async def create_workload_request_decision_route(
         data: WorkloadRequestDecisionCreate, db_session: AsyncSession = Depends(get_async_db)):
    """
        Create a new WorkloadRequestDecision entry.

        Args:
            data (WorkloadRequestDecisionSchema): The pod decision data to create.
            db_session (AsyncSession): Database session dependency.

        Returns:
            WorkloadRequestDecisionSchema: The newly created pod decision.
    """
    return await create_workload_decision(db_session, data)


@router.get(path="/{decision_id}", response_model= WorkloadRequestDecisionSchema)
async def get_workload_decision_route(decision_id: UUID,
                                 db_session: AsyncSession = Depends(get_async_db)):
    """
       Retrieve a single WorkloadDecision by ID.

       Args:
           decision_id (UUID): The ID of the pod decision to retrieve.
           db_session (AsyncSession): Database session dependency.

       Returns:
           PodRequestDecisionSchema: The pod decision with the given ID.
    """
    return await get_workload_decision(db_session, decision_id)


@router.get("/", response_model=list[WorkloadRequestDecisionSchema])
async def get_all_workload_decisions_route(
        db_session: AsyncSession = Depends(get_async_db), skip: int = Query(0, ge=0),
        limit: int = Query(100, gt=0, le=1000)):
    """
        Retrieve all WorkloadRequestDecisions with pagination.

        Args:
            db_session (AsyncSession): Database session dependency.
            skip (int): Number of records to skip for pagination.
            limit (int): Maximum number of records to return.

        Returns:
            List[WorkloadRequestDecisionSchema]: List of pod decisions.
    """
    return await get_all_workload_decisions(db_session, skip, limit)


@router.put(path="/{decision_id}", response_model=WorkloadRequestDecisionUpdate)
async def update_workload_decision_route(decision_id: UUID,
                                    data: WorkloadRequestDecisionUpdate,
                                    db_session: AsyncSession = Depends(get_async_db)):
    """
        Update an existing WorkloadRequestDecision by ID.

        Args:
            decision_id (UUID): The ID of the pod decision to update.
            data (WorkloadRequestDecisionUpdate): Fields to update.
            db_session (AsyncSession): Database session dependency.

        Returns:
            WorkloadDecisionSchema: The updated pod decision.
    """
    return await update_workload_decision(db_session, decision_id, data)


@router.delete(path="/{decision_id}")
async def delete_workload_decision_route(decision_id: UUID,
                                    db_session: AsyncSession = Depends(get_async_db)):
    """
        Delete a WorkloadRequestDecision by ID.

        Args:
            decision_id (UUID): The ID of the pod decision to delete.
            db_session (AsyncSession): Database session dependency.

        Returns:
            dict: Confirmation of deletion or relevant error message.
    """
    return await delete_workload_decision(db_session, decision_id)
