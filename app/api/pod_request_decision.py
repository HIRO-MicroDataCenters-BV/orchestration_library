"""
DB pod decision routes.
This module defines the API endpoints for managing nodes in the database.
It includes routes for creating, retrieving, updating, and deleting nodes.
"""
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_async_db
from app.schemas.pod_request_decision import (
    PodRequestDecisionUpdate,
    PodRequestDecisionSchema,
    PodRequestDecisionCreate
)
from app.repositories.pod_request_decision import (
    create_pod_decision,
    get_all_pod_decisions,
    get_pod_decision,
    update_pod_decision,
    delete_pod_decision
)

router = APIRouter(prefix="/pod_request_decision", tags=["Pod Request Decision"])


@router.post(path="/", response_model=PodRequestDecisionSchema)
async def create_pod_request_decision_route(
         data: PodRequestDecisionCreate, db_session: AsyncSession = Depends(get_async_db)):
    """
        Create a new PodRequestDecision entry.

        Args:
            data (PodRequestDecisionSchema): The pod decision data to create.
            db_session (AsyncSession): Database session dependency.

        Returns:
            PodRequestDecisionSchema: The newly created pod decision.
    """
    return await create_pod_decision(db_session, data)


@router.get(path="/{pod_decision_id}", response_model= PodRequestDecisionSchema)
async def get_pod_decision_route(pod_decision_id: UUID,
                                 db_session: AsyncSession = Depends(get_async_db)):
    """
       Retrieve a single PodRequestDecision by ID.

       Args:
           pod_decision_id (UUID): The ID of the pod decision to retrieve.
           db_session (AsyncSession): Database session dependency.

       Returns:
           PodRequestDecisionSchema: The pod decision with the given ID.
    """
    return await get_pod_decision(db_session, pod_decision_id)


@router.get("/", response_model=list[PodRequestDecisionSchema])
async def get_all_pod_decisions_route(
        db_session: AsyncSession = Depends(get_async_db), skip: int = Query(0, ge=0),
        limit: int = Query(100, gt=0, le=1000)):
    """
        Retrieve all PodRequestDecisions with pagination.

        Args:
            db_session (AsyncSession): Database session dependency.
            skip (int): Number of records to skip for pagination.
            limit (int): Maximum number of records to return.

        Returns:
            List[PodRequestDecisionSchema]: List of pod decisions.
    """
    return await get_all_pod_decisions(db_session, skip, limit)


@router.put(path="/{pod_decision_id}", response_model=PodRequestDecisionUpdate)
async def update_pod_decision_route(pod_decision_id: UUID,
                                    data: PodRequestDecisionUpdate,
                                    db_session: AsyncSession = Depends(get_async_db)):
    """
        Update an existing PodRequestDecision by ID.

        Args:
            pod_decision_id (UUID): The ID of the pod decision to update.
            data (PodRequestDecisionUpdate): Fields to update.
            db_session (AsyncSession): Database session dependency.

        Returns:
            PodRequestDecisionSchema: The updated pod decision.
    """
    return await update_pod_decision(db_session, pod_decision_id, data)


@router.delete(path="/{pod_decision_id}")
async def delete_pod_decision_route(pod_decision_id: UUID,
                                    db_session: AsyncSession = Depends(get_async_db)):
    """
        Delete a PodRequestDecision by ID.

        Args:
            pod_decision_id (UUID): The ID of the pod decision to delete.
            db_session (AsyncSession): Database session dependency.

        Returns:
            dict: Confirmation of deletion or relevant error message.
    """
    return await delete_pod_decision(db_session, pod_decision_id)
