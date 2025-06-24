"""
DB pod decision routes.
This module defines the API endpoints for managing nodes in the database.
It includes routes for creating, retrieving, updating, and deleting nodes.
"""
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_async_db
from app.schemas.workload_decision_schema import (
    WorkloadDecisionUpdate,
    WorkloadDecisionSchema,
    WorkloadDecisionCreate
)
from app.repositories.workload_decision import (
    create_pod_decision,
    get_all_pod_decisions,
    get_pod_decision,
    update_pod_decision,
    delete_pod_decision
)

router = APIRouter(prefix="/workload_decision", tags=["Workload Decision"])


@router.post(path="/", response_model=WorkloadDecisionSchema)
async def create_pod_request_decision_route(
         data: WorkloadDecisionCreate, db_session: AsyncSession = Depends(get_async_db)):
    """
        Create a new WorkloadDecision entry.

        Args:
            data (PodRequestDecisionSchema): The pod decision data to create.
            db_session (AsyncSession): Database session dependency.

        Returns:
            PodRequestDecisionSchema: The newly created pod decision.
    """
    return await create_pod_decision(db_session, data)


@router.get(path="/{decision_id}", response_model= WorkloadDecisionSchema)
async def get_pod_decision_route(decision_id: UUID,
                                 db_session: AsyncSession = Depends(get_async_db)):
    """
       Retrieve a single WorkloadDecision by ID.

       Args:
           decision_id (UUID): The ID of the pod decision to retrieve.
           db_session (AsyncSession): Database session dependency.

       Returns:
           PodRequestDecisionSchema: The pod decision with the given ID.
    """
    return await get_pod_decision(db_session, decision_id)


@router.get("/", response_model=list[WorkloadDecisionSchema])
async def get_all_pod_decisions_route(
        db_session: AsyncSession = Depends(get_async_db), skip: int = Query(0, ge=0),
        limit: int = Query(100, gt=0, le=1000)):
    """
        Retrieve all WorkloadDecisions with pagination.

        Args:
            db_session (AsyncSession): Database session dependency.
            skip (int): Number of records to skip for pagination.
            limit (int): Maximum number of records to return.

        Returns:
            List[WorkloadDecisionSchema]: List of pod decisions.
    """
    return await get_all_pod_decisions(db_session, skip, limit)


@router.put(path="/{decision_id}", response_model=WorkloadDecisionUpdate)
async def update_pod_decision_route(decision_id: UUID,
                                    data: WorkloadDecisionUpdate,
                                    db_session: AsyncSession = Depends(get_async_db)):
    """
        Update an existing WorkloadDecision by ID.

        Args:
            decision_id (UUID): The ID of the pod decision to update.
            data (WorkloadDecisionUpdate): Fields to update.
            db_session (AsyncSession): Database session dependency.

        Returns:
            WorkloadDecisionSchema: The updated pod decision.
    """
    return await update_pod_decision(db_session, decision_id, data)


@router.delete(path="/{decision_id}")
async def delete_pod_decision_route(decision_id: UUID,
                                    db_session: AsyncSession = Depends(get_async_db)):
    """
        Delete a WorkloadDecision by ID.

        Args:
            decision_id (UUID): The ID of the pod decision to delete.
            db_session (AsyncSession): Database session dependency.

        Returns:
            dict: Confirmation of deletion or relevant error message.
    """
    return await delete_pod_decision(db_session, decision_id)
