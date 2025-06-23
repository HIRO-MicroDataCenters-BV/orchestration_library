"""
CRUD operations for pod request decision in the database.
"""

import logging

from uuid import UUID

from sqlalchemy.exc import SQLAlchemyError, IntegrityError, OperationalError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.pod_request_decision import PodRequestDecision
from app.schemas.pod_request_decision import (
    PodRequestDecisionUpdate,
    PodRequestDecisionCreate,
)
from app.utils.db_utils import handle_db_exception
from app.utils.exceptions import (
    DBEntryCreationException,
    BaseException,
    DBEntryUpdateException,
    DBEntryDeletionException,
    DBEntryNotFoundException,
)


# Configure logger
logger = logging.getLogger(__name__)


async def create_pod_decision(db_session: AsyncSession, data: PodRequestDecisionCreate):
    """
    Create a new PodRequestDecision record in the database.

    Args:
        db_session (AsyncSession): The async SQLAlchemy database session.
        data (PodRequestDecisionCreate): The data for the new pod decision.

    Returns:
        PodRequestDecision: The created pod decision ORM object.

    Raises:
        DBEntryCreationException: If creation fails due to integrity or DB errors.
    """
    try:
        db_obj = PodRequestDecision(**data.dict())
        db_session.add(db_obj)
        await db_session.commit()
        await db_session.refresh(db_obj)
        logger.info("successfully created pod decision with %s", data.pod_name)
        return db_obj
    except IntegrityError as exc:
        await db_session.rollback()
        logger.error(
            "Integrity error while creating pod decision %s %s", data.pod_name, str(exc)
        )
        raise DBEntryCreationException(
            message=f"Failed to create pod decision"
            f"'{data.pod_name}': Data constraint violation",
            details={
                "error_type": "pod_request_decision_database_integrity_error",
                "error": str(exc),
            },
        ) from exc
    except OperationalError as exc:
        await handle_db_exception(
            exc,
            db_session,
            logger,
            exception_details={
                "message": 
                f"Failed to create pod_decision with name '{data.pod_name}'",
                "pod_name": data.pod_name,
                "error": str(exc),
                "error_type": "pod_request_decision_database_connection_error",
            },
            custom_exception_cls=DBEntryCreationException,
        )
    except SQLAlchemyError as exc:
        await handle_db_exception(
            exc,
            db_session,
            logger,
            exception_details={
                "message": 
                f"Failed to create pod_decision with pod '{data.pod_name}'",
                "pod_name": data.pod_name,
                "error": str(exc),
                "error_type": "database_error",
            },
            custom_exception_cls=DBEntryCreationException,
        )


async def get_pod_decision(db_session: AsyncSession, pod_decision_id: UUID):
    """
    Retrieve a specific PodRequestDecision by its ID.

    Args:
        db_session (AsyncSession): The async SQLAlchemy database session.
        pod_decision_id (UUID): The ID of the pod decision to retrieve.

    Returns:
        PodRequestDecision: The pod decision ORM object if found.

    Raises:
        DBEntryNotFoundException: If the pod decision is not found.
        DataBaseException: For database-related errors.
    """
    try:
        result = await db_session.execute(
            select(PodRequestDecision).where(PodRequestDecision.id == pod_decision_id)
        )
        pod_decision = result.scalar_one_or_none()

        if not pod_decision:
            raise DBEntryNotFoundException(
                message=f"Pod decision with id '{pod_decision_id}' not found."
            )

        return pod_decision
    except OperationalError as exc:
        logger.error(
            "Database operational error while retrieving pod decision : %s", str(exc)
        )
        raise BaseException(
            message="Failed to retrieve pod decision : Database connection error",
            details={"error_type": "database_connection_error", "error": str(exc)},
        ) from exc
    except SQLAlchemyError as exc:
        logger.error("Database error while retrieving pod decision : %s", str(exc))
        raise BaseException(
            message="Failed to retrieve pod decision: Database error",
            details={"error_type": "database_error", "error": str(exc)},
        ) from exc


async def get_all_pod_decisions(
    db_session: AsyncSession, skip: int = 0, limit: int = 100
):
    """
    Retrieve all PodRequestDecision records with pagination.

    Args:
        db_session (AsyncSession): The async SQLAlchemy database session.
        skip (int): Number of records to skip.
        limit (int): Maximum number of records to retrieve.

    Returns:
        List[PodRequestDecision]: A list of pod decision ORM objects.

    Raises:
        DataBaseException: If a database error occurs during retrieval.
    """
    try:
        result = await db_session.execute(
            select(PodRequestDecision).offset(skip).limit(limit)
        )
        return result.scalars().all()
    except SQLAlchemyError as exc:
        logger.error("Error retrieving all pod decisions %s", str(exc))
        raise BaseException(
            message="Failed to retrieve pod decisions due to database error.",
            details={"error": str(exc)},
        ) from exc


async def update_pod_decision(
    db_session: AsyncSession, pod_decision_id: UUID, data: PodRequestDecisionUpdate
):
    """
    Update an existing PodRequestDecision record by its ID.

    Args:
        db_session (AsyncSession): The async SQLAlchemy database session.
        pod_decision_id (UUID): The ID of the pod decision to update.
        data (PodRequestDecisionUpdate): Fields to update in the record.

    Returns:
        PodRequestDecision: The updated pod decision ORM object.

    Raises:
        DBEntryNotFoundException: If the pod decision is not found.
        DBEntryUpdateException: If update fails due to integrity or DB errors.
    """
    try:
        result = await db_session.execute(
            select(PodRequestDecision).where(PodRequestDecision.id == pod_decision_id)
        )
        pod_decision = result.scalar_one_or_none()

        if not pod_decision:
            raise DBEntryNotFoundException(
                message=f"Pod decision with id '{pod_decision_id}' not found."
            )

        for key, value in data.dict().items():
            setattr(pod_decision, key, value)

        await db_session.commit()
        await db_session.refresh(pod_decision)
        logger.info("Successfully updated pod decision %s", pod_decision_id)
        return pod_decision

    except IntegrityError as exc:
        await db_session.rollback()
        logger.error(
            "Integrity error while updating pod decision %s %s",
            pod_decision_id,
            str(exc),
        )
        raise DBEntryUpdateException(
            message="Failed to update pod decision due to integrity error.",
            details={"error": str(exc)},
        ) from exc
    except OperationalError as exc:
        await db_session.rollback()
        logger.error(
            "Database operational error while updating pod decision %s: %s",
            pod_decision_id,
            str(exc),
        )
        raise DBEntryUpdateException(
            message=f"Failed to update pod decision {pod_decision_id}: Database connection error",
            details={
                "error_type": "database_connection_error",
                "error": str(exc),
                "pod_decision_id": str(pod_decision_id),
            },
        ) from exc
    except SQLAlchemyError as exc:
        await db_session.rollback()
        logger.error(
            "SQL error while updating pod decision %s %s ", pod_decision_id, str(exc)
        )
        raise DBEntryUpdateException(
            message="Failed to update pod decision due to database error.",
            details={"error": str(exc)},
        ) from exc


async def delete_pod_decision(db_session: AsyncSession, pod_decision_id: UUID):
    """
    Delete a PodRequestDecision record by its ID.

    Args:
        db_session (AsyncSession): The async SQLAlchemy database session.
        pod_decision_id (UUID): The ID of the pod decision to delete.

    Returns:
        bool: True if deletion is successful.

    Raises:
        DBEntryNotFoundException: If the pod decision is not found.
        DBEntryDeletionException: If deletion fails due to DB errors.
    """
    try:
        result = await db_session.execute(
            select(PodRequestDecision).where(PodRequestDecision.id == pod_decision_id)
        )
        pod_decision = result.scalar_one_or_none()

        if not pod_decision:
            raise DBEntryNotFoundException(
                message=f"Pod decision with id '{pod_decision_id}' not found."
            )

        await db_session.delete(pod_decision)
        await db_session.commit()
        logger.info("Successfully deleted pod decision %s", pod_decision_id)
        return True

    except IntegrityError as exc:
        await db_session.rollback()
        logger.error(
            "Integrity error while deleting pod decision %s: %s",
            pod_decision_id,
            str(exc),
        )
        raise DBEntryDeletionException(
            message=f"Failed to delete pod decision {pod_decision_id}: Data constraint violation",
            details={
                "error_type": "database_integrity_error",
                "error": str(exc),
                "pod_decision_id": str(pod_decision_id),
            },
        ) from exc
    except OperationalError as exc:
        await db_session.rollback()
        logger.error(
            "Database operational error while deleting pod decision %s: %s",
            pod_decision_id,
            str(exc),
        )
        raise DBEntryDeletionException(
            message=f"Failed to delete pod decision {pod_decision_id}: Database connection error",
            details={
                "error_type": "database_connection_error",
                "error": str(exc),
                "pod_decision_id": str(pod_decision_id),
            },
        ) from exc
    except SQLAlchemyError as exc:
        await db_session.rollback()
        logger.error(
            "Database error while deleting pod decision %s: %s",
            pod_decision_id,
            str(exc),
        )
        raise DBEntryDeletionException(
            message=f"Failed to delete pod decision {pod_decision_id}: Database error",
            details={
                "error_type": "database_error",
                "error": str(exc),
                "pod_decision_id": str(pod_decision_id),
            },
        ) from exc
