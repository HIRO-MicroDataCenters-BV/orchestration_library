import logging

from sqlalchemy.exc import SQLAlchemyError, IntegrityError, OperationalError
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.pod_request_decision import PodRequestDecision
from app.schemas.pod_request_decision import PodRequestDecisionUpdate, PodRequestDecisionSchema
from app.utils.exceptions import (
    DBEntryCreationException,
    DataBaseException,
    DBEntryUpdateException,
    DBEntryDeletionException,
    DBEntryNotFoundException
)


# Configure logger
logger = logging.getLogger(__name__)


async def create_pod_decision(db_session: AsyncSession, data: PodRequestDecisionSchema):
    try:
        db_obj = PodRequestDecision(**data.dict())
        db_session.add(db_obj)
        await db_session.commit()
        await db_session.refresh(db_obj)
        logger.info(f"successfully created pod decision with {data.pod_name}")
        return db_obj
    except IntegrityError as exc:
        await db_session.rollback()
        logger.error(f"Integrity error while creating pod decision {data.pod_name}: {str(exc)}")
        raise DBEntryCreationException(
            message=f"Failed to create pod decision with name '{data.pod_name}': Data constraint violation",
            details={
                "error_type": "database_integrity_error",
                "error": str(exc)
            }
        ) from exc
    except OperationalError as exc:
        await db_session.rollback()
        logger.error("Database operational error while creating pod_decision %s: %s", data.pod_name, str(exc))
        raise DBEntryCreationException(
            message=f"Failed to create pod_decision with name '{data.pod_name}': Database connection error",
            details={
                "error_type": "database_connection_error",
                "error": str(exc)
            }
        ) from exc
    except SQLAlchemyError as exc:
        await db_session.rollback()
        logger.error("Database error while creating pod_decision %s: %s", data.name, str(e))
        raise DBEntryCreationException(
            message=f"Failed to create pod_decision with pod '{data.pod_name}': Database error",
            details={
                "error_type": "database_error",
                "error": str(exc)
            }
        ) from exc


async def get_pod_decision(db_session: AsyncSession, pod_decision_id: UUID):
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
        logger.error("Database operational error while retrieving pod decision : %s", str(exc))
        raise DataBaseException(
            message="Failed to retrieve pod decision : Database connection error",
            details={
                "error_type": "database_connection_error",
                "error": str(exc)
            }
        ) from exc
    except SQLAlchemyError as exc:
        logger.error("Database error while retrieving pod decision : %s", str(exc))
        raise DataBaseException(
            message="Failed to retrieve pod decision: Database error",
            details={
                "error_type": "database_error",
                "error": str(exc)
            }
        ) from exc


async def get_all_pod_decisions(db_session: AsyncSession, skip: int = 0, limit: int = 100):
    try:
        result = await db_session.execute(
            select(PodRequestDecision).offset(skip).limit(limit)
        )
        return result.scalars().all()
    except SQLAlchemyError as exc:
        logger.error(f"Error retrieving all pod decisions: {str(exc)}")
        raise DataBaseException(
            message="Failed to retrieve pod decisions due to database error.",
            details={"error": str(exc)}
        ) from exc


async def update_pod_decision(db_session: AsyncSession, pod_decision_id: UUID, data: PodRequestDecisionUpdate):
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
        logger.info(f"Successfully updated pod decision {pod_decision_id}")
        return pod_decision

    except IntegrityError as exc:
        await db_session.rollback()
        logger.error(f"Integrity error while updating pod decision {pod_decision_id}: {str(exc)}")
        raise DBEntryUpdateException(
            message="Failed to update pod decision due to integrity error.",
            details={"error": str(exc)}
        ) from exc
    except OperationalError as exc:
        await db_session.rollback()
        logger.error("Database operational error while updating pod decision %s: %s", pod_decision_id, str(exc))
        raise DBEntryUpdateException(
            message=f"Failed to update pod decision {pod_decision_id}: Database connection error",
            details={
                "error_type": "database_connection_error",
                "error": str(exc),
                "pod_decision_id": str(pod_decision_id)
            }
        ) from exc
    except SQLAlchemyError as exc:
        await db_session.rollback()
        logger.error(f"SQL error while updating pod decision {pod_decision_id}: {str(exc)}")
        raise DBEntryUpdateException(
            message="Failed to update pod decision due to database error.",
            details={"error": str(exc)}
        ) from exc


async def delete_pod_decision(db_session: AsyncSession, pod_decision_id: UUID):
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
        logger.info(f"Successfully deleted pod decision {pod_decision_id}")
        return True

    except IntegrityError as exc:
        await db_session.rollback()
        logger.error("Integrity error while deleting pod decision %s: %s", pod_decision_id, str(exc))
        raise DBEntryDeletionException(
            message=f"Failed to delete pod decision {pod_decision_id}: Data constraint violation",
            details={
                "error_type": "database_integrity_error",
                "error": str(exc),
                "pod_decision_id": str(pod_decision_id)
            }
        ) from exc
    except OperationalError as exc:
        await db_session.rollback()
        logger.error("Database operational error while deleting pod decision %s: %s", pod_decision_id, str(exc))
        raise DBEntryDeletionException(
            message=f"Failed to delete pod decision {pod_decision_id}: Database connection error",
            details={
                "error_type": "database_connection_error",
                "error": str(exc),
                "pod_decision_id": str(pod_decision_id)
            }
        ) from exc
    except SQLAlchemyError as exc:
        await db_session.rollback()
        logger.error("Database error while deleting pod decision %s: %s", pod_decision_id, str(exc))
        raise DBEntryDeletionException(
            message=f"Failed to delete pod decision {pod_decision_id}: Database error",
            details={
                "error_type": "database_error",
                "error": str(exc),
                "pod_decision_id": str(pod_decision_id)
            }
        ) from exc

