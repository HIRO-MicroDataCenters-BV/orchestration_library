"""
CRUD operations for managing workload requests in the database.
"""

import logging
from dataclasses import dataclass
from math import log
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, OperationalError
from sqlalchemy import select
from app.models.workload_request import WorkloadRequest
from app.schemas.workload_request import WorkloadRequestCreate
from app.utils.exceptions import (
    DBEntryCreationException,
    DBEntryDeletionException,
    DBEntryNotFoundException,
    DBEntryUpdateException,
    DataBaseException,
)

logger = logging.getLogger(__name__)


@dataclass
class WorkloadRequestFilter:
    """
    Data class for filtering workload requests.
    This class can be extended with additional filter fields as needed.
    """

    workload_request_id: UUID = None
    name: str = None
    namespace: str = None
    api_version: str = None
    kind: str = None
    status: str = None
    current_scale: int = None


async def create_workload_request(db: AsyncSession, req: WorkloadRequestCreate):
    """
    Create a new workload request.
    """
    try:
        obj = WorkloadRequest(**req.model_dump())
        db.add(obj)
        await db.commit()
        await db.refresh(obj)
        return obj
    except IntegrityError as e:
        await db.rollback()
        logger.error(
            "Integrity error while creating workload request %s: %s", req.name, str(e)
        )
        raise DBEntryCreationException(
            message=f"Failed to create workload request '{req.name}' : {str(e)}",
            details={"error": str(e), "request_data": req.model_dump()},
        ) from e
    except OperationalError as e:
        await db.rollback()
        logger.error(
            "Database operational error while creating workload request %s: %s",
            req.name,
            str(e),
        )
        raise DBEntryCreationException(
            message=f"Database connection error while creating workload request '{req.name}'",
            details={"error": str(e), "request_data": req.model_dump()},
        ) from e
    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(
            "SQLAlchemy error while creating workload request %s: %s", req.name, str(e)
        )
        raise DBEntryCreationException(
            message=f"Failed to create workload request '{req.name}'",
            details={"error": str(e), "request_data": req.model_dump()},
        ) from e


async def get_workload_requests(db: AsyncSession, wrfilter: WorkloadRequestFilter):
    """
    Get workload requests based on various optional filters.
    """
    try:
        filters = []
        if wrfilter.workload_request_id:
            filters.append(WorkloadRequest.id == wrfilter.workload_request_id)
        if wrfilter.name:
            filters.append(WorkloadRequest.name == wrfilter.name)
        if wrfilter.namespace:
            filters.append(WorkloadRequest.namespace == wrfilter.namespace)
        if wrfilter.api_version:
            filters.append(WorkloadRequest.api_version == wrfilter.api_version)
        if wrfilter.kind:
            filters.append(WorkloadRequest.kind == wrfilter.kind)
        if wrfilter.status:
            filters.append(WorkloadRequest.status == wrfilter.status)
        if wrfilter.current_scale is not None:
            filters.append(WorkloadRequest.current_scale == wrfilter.current_scale)

        query = (
            select(WorkloadRequest).where(*filters)
            if filters
            else select(WorkloadRequest)
        )
        result = await db.execute(query)

        workload_requests = result.scalars().all()
        if not workload_requests:
            logger.warning(
                "No workload requests found with the provided filters: %s", wrfilter
            )
            raise DBEntryNotFoundException(
                "No workload requests found",
                details={"filters": wrfilter.model_dump()},
            )
        logger.info("Retrieved %d workload requests", len(workload_requests))
        return workload_requests
    except OperationalError as e:
        raise DataBaseException(
            "Database connection error while retrieving workload requests",
            details={"error": str(e)},
        ) from e
    except SQLAlchemyError as e:
        raise DataBaseException(
            "Failed to retrieve workload requests",
            details={"error": str(e)},
        ) from e


async def update_workload_request(
    db: AsyncSession, workload_request_id: UUID, updates: dict
):
    """
    Update a WorkloadRequest based on its ID.
    """
    try:
        result = await db.execute(
            select(WorkloadRequest).where(WorkloadRequest.id == workload_request_id)
        )
        workload_request = result.scalar_one_or_none()

        if not workload_request:
            logger.warning(
                "WorkloadRequest with ID %s not found for update", workload_request_id
            )
            raise DBEntryNotFoundException(
                f"WorkloadRequest with ID {workload_request_id} not found",
                details={
                    "error": "NotFoundError",
                    "workload_request_id": str(workload_request_id),
                },
            )

        for key, value in updates.items():
            if hasattr(workload_request, key):
                setattr(workload_request, key, value)

        db.add(workload_request)
        await db.commit()
        await db.refresh(workload_request)

        return workload_request
    except IntegrityError as e:
        await db.rollback()
        logger.error(
            "Integrity error while updating workload request %s: %s",
            workload_request_id,
            str(e),
        )
        raise DBEntryUpdateException(
            "Failed to update workload request",
            details={
                "error": str(e),
                "workload_request_id": str(workload_request_id),
            },
        ) from e
    except OperationalError as e:
        await db.rollback()
        logger.error(
            "Database operational error while updating workload request %s: %s",
            workload_request_id,
            str(e),
        )
        raise DBEntryUpdateException(
            "Database connection error during workload request update",
            details={
                "error": str(e),
                "workload_request_id": str(workload_request_id),
            },
        ) from e
    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(
            "SQLAlchemy error while updating workload request %s: %s",
            workload_request_id,
            str(e),
        )
        raise DBEntryUpdateException(
            "Failed to update workload request",
            details={
                "error": str(e),
                "workload_request_id": str(workload_request_id),
            },
        ) from e


async def delete_workload_request(db: AsyncSession, workload_request_id: UUID):
    """
    Delete a WorkloadRequest by its ID.
    Args:
        db (AsyncSession): SQLAlchemy async session.
        workload_request_id (UUID): ID of the workload request to delete.
    Returns:
        dict: Success message with deleted workload request ID.
    Raises:
        DBEntryNotFoundException: If the workload request does not exist.
        DBEntryDeletionException: On delete failure.
    """
    try:
        result = await db.execute(
            select(WorkloadRequest).where(WorkloadRequest.id == workload_request_id)
        )
        workload_request = result.scalar_one_or_none()

        if not workload_request:
            logger.warning(
                "WorkloadRequest with ID %s not found for deletion", workload_request_id
            )
            raise DBEntryNotFoundException(
                f"WorkloadRequest with ID {workload_request_id} not found",
                details={
                    "error": "NotFoundError",
                    "workload_request_id": str(workload_request_id),
                },
            )
        logger.info("Deleting WorkloadRequest with ID %s", workload_request_id)

        await db.delete(workload_request)
        await db.commit()

        return {
            "message": f"WorkloadRequest with ID {workload_request_id} has been deleted"
        }
    except IntegrityError as e:
        await db.rollback()
        logger.error(
            "Integrity error while deleting workload request %s: %s",
            workload_request_id,
            str(e),
        )
        raise DBEntryDeletionException(
            "Failed to delete workload request",
            details={
                "error": str(e),
                "workload_request_id": str(workload_request_id),
            },
        ) from e
    except OperationalError as e:
        await db.rollback()
        logger.error(
            "Database operational error while deleting workload request %s: %s",
            workload_request_id,
            str(e),
        )
        raise DBEntryDeletionException(
            "Database connection error during workload request deletion",
            details={
                "error": str(e),
                "workload_request_id": str(workload_request_id),
            },
        ) from e
    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(
            "SQLAlchemy error while deleting workload request %s: %s",
            workload_request_id,
            str(e),
        )
        raise DBEntryCreationException(
            "Failed to delete workload request", details={"error": str(e)}
        ) from e
