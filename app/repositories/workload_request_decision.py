"""
CRUD operations for managing workload request decission in the database.
"""

from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select
from app.models.workload_request_decision import WorkloadRequestDecision
from app.schemas.workload_request_decision import WorkloadRequestDecisionCreate
from app.utils.exceptions import (
    DBEntryCreationException,
    DBEntryUpdateException,
    DBEntryNotFoundException,
    DBEntryDeletionException,
    DatabaseConnectionException,
)


# pylint: disable=invalid-name
async def create_workload_request_decision(
    db: AsyncSession, decision: WorkloadRequestDecisionCreate
):
    """
    Create a new workload request decision.
    """
    try:
        obj = WorkloadRequestDecision(**decision.model_dump())
        db.add(obj)
        await db.commit()
        await db.refresh(obj)
        return obj
    except SQLAlchemyError as e:
        raise DBEntryCreationException(
            "Failed to create workload request decision", details={"error": str(e)}
        ) from e
    except Exception as e:
        raise DatabaseConnectionException(
            "Unexpected error during workload request decision creation",
            details={"error": str(e)},
        ) from e


async def update_workload_request_decision(
    db: AsyncSession, pod_id: UUID, updates: dict
):
    """
    Update a workload request decision by its pod_id.
    """
    try:
        result = await db.execute(
            select(WorkloadRequestDecision).where(
                WorkloadRequestDecision.pod_id == pod_id
            )
        )
        decision = result.scalar_one_or_none()
        if not decision:
            raise DBEntryNotFoundException(
                f"Workload request decision not found for pod_id: {pod_id}"
            )

        for key, value in updates.items():
            if hasattr(decision, key):
                setattr(decision, key, value)

        db.add(decision)
        await db.commit()
        await db.refresh(decision)
        return decision
    except SQLAlchemyError as e:
        raise DBEntryUpdateException(
            "Failed to update workload request decision", details={"error": str(e)}
        ) from e
    except Exception as e:
        raise DatabaseConnectionException(
            "Unexpected error during workload request decision update",
            details={"error": str(e)},
        ) from e


async def get_workload_request_decision(
    db: AsyncSession,
    pod_id: UUID = None,
    node_name: str = None,
    queue_name: str = None,
    status: str = None,
):
    """
    Get workload request decisions based on various filters.
    """
    try:
        filters = []
        if pod_id:
            filters.append(WorkloadRequestDecision.pod_id == pod_id)
        if node_name:
            filters.append(WorkloadRequestDecision.node_name == node_name)
        if queue_name:
            filters.append(WorkloadRequestDecision.queue_name == queue_name)
        if status:
            filters.append(WorkloadRequestDecision.status == status)
        if filters:
            query = select(WorkloadRequestDecision).where(*filters)
        else:
            query = select(WorkloadRequestDecision)

        result = await db.execute(query)
        decision = result.scalars().all()
        return decision
    except SQLAlchemyError as e:
        raise DatabaseConnectionException(
            "Database error occurred while fetching workload request decision(s)",
            details={"error": str(e)},
        ) from e


async def delete_workload_request_decision(db: AsyncSession, pod_id: UUID):
    """
    Delete a workload request decision by its pod_id.
    """
    try:
        decision = await get_workload_request_decision(db, pod_id=pod_id)
        print(f"Decision: {decision}")
        if not decision:
            raise DBEntryNotFoundException(
                f"Workload request decision not found for pod_id: {pod_id}"
            )

        if isinstance(decision, list):
            for dec in decision:
                await db.delete(dec)
        else:
            await db.delete(decision)
        await db.commit()
        return {"message": f"Decision with ID {pod_id} has been deleted"}
    except SQLAlchemyError as e:
        raise DBEntryDeletionException(
            "Failed to delete workload request decision", details={"error": str(e)}
        ) from e
    except Exception as e:
        raise DatabaseConnectionException(
            "Unexpected error during workload request decision deletion",
            details={"error": str(e)},
        ) from e
