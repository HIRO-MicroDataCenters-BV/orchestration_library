"""
Routes for managing workload request decisions.
"""

from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from app.repositories import workload_request_decision as wrd
from app.db.database import get_async_db
from app.schemas.workload_request_decision import (
    WorkloadRequestDecisionCreate,
    WorkloadRequestDecisionUpdate,
)
from app.utils.exceptions import (
    DatabaseConnectionException,
    DBEntryCreationException,
    DBEntryNotFoundException,
    DBEntryUpdateException,
    DBEntryDeletionException,
)

router = APIRouter(prefix="/workload_request_decision")

# pylint: disable=invalid-name
@router.post("/")
async def create(
    data: WorkloadRequestDecisionCreate,
    db: AsyncSession = Depends(get_async_db),
):
    """
    Create a new workload request decision.
    """
    try:
        return await wrd.create_workload_request_decision(db, data)
    except SQLAlchemyError as e:
        raise DBEntryCreationException(
            "Failed to create workload request decision", details={"error": str(e)}
        ) from e
    except Exception as e:
        raise DatabaseConnectionException(
            "Unexpected error during workload request decision creation",
            details={"error": str(e)},
        ) from e


@router.get("/")
async def read(
    pod_id: UUID = None,
    node_name: str = None,
    queue_name: str = None,
    status: str = None,
    db: AsyncSession = Depends(get_async_db),
):
    """
    Retrieve workload request decisions based on various filters.
    If no filters are provided, return all decisions.
    """
    try:
        decisions = await wrd.get_workload_request_decision(
            db,
            pod_id=pod_id,
            node_name=node_name,
            queue_name=queue_name,
            status=status,
        )
        if not decisions:
            raise DBEntryNotFoundException("No workload request decisions found")
        return decisions
    except SQLAlchemyError as e:
        raise DatabaseConnectionException(
            "Failed to retrieve workload request decisions", details={"error": str(e)}
        ) from e


@router.get("/{pod_id}")
async def read_by_id(pod_id: UUID, db: AsyncSession = Depends(get_async_db)):
    """
    Retrieve a workload request decision by its ID.
    """
    try:
        decision = await wrd.get_workload_request_decision(db, pod_id=pod_id)
        if not decision:
            raise DBEntryNotFoundException(
                f"Decision with pod_id {pod_id} not found",
                details={"pod_id": str(pod_id)},
            )
        return decision
    except SQLAlchemyError as e:
        raise DatabaseConnectionException(
            f"Failed to retrieve workload request decision with pod_id {pod_id}",
            details={"error": str(e)},
        ) from e


@router.put("/{pod_id}")
async def update(
    pod_id: UUID,
    data: WorkloadRequestDecisionUpdate,
    db: AsyncSession = Depends(get_async_db),
):
    """
    Update a workload request decision by its ID.
    """
    try:
        updated = await wrd.update_workload_request_decision(db, pod_id, data)
        if not updated:
            raise DBEntryUpdateException(
                f"Failed to update decision with pod_id {pod_id}",
                details={"pod_id": str(pod_id)},
            )
        return updated
    except SQLAlchemyError as e:
        raise DatabaseConnectionException(
            f"Database error while updating decision with pod_id {pod_id}",
            details={"error": str(e)},
        ) from e


@router.delete("/{pod_id}")
async def delete(pod_id: UUID, db: AsyncSession = Depends(get_async_db)):
    """
    Delete a workload request decision by its ID.
    """
    try:
        result = await wrd.delete_workload_request_decision(db, pod_id=pod_id)
        if "error" in result:
            raise DBEntryDeletionException(
                f"Failed to delete decision with pod_id {pod_id}",
                details={"pod_id": str(pod_id)},
            )
        return result
    except SQLAlchemyError as e:
        raise DatabaseConnectionException(
            f"Database error while deleting decision with pod_id {pod_id}",
            details={"error": str(e)},
        ) from e
