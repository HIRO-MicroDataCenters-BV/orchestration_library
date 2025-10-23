"""
CRUD operations for managing alerts in the database.
"""

import logging
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, OperationalError
from sqlalchemy.ext.asyncio import AsyncSession

from app.metrics.helper import record_alerts_metrics
from app.models.alerts import Alert
from app.repositories.k8s.k8s_pod import delete_k8s_user_pod
from app.schemas.alerts_request import AlertCreateRequest, AlertResponse
from app.utils.exceptions import (
    DBEntryCreationException, OrchestrationBaseException
)

logger = logging.getLogger(__name__)


async def create_alert(
        db: AsyncSession, alert: AlertCreateRequest, metrics_details: dict = None
) -> AlertResponse:
    """
    Create a new alert in the database.

    Args:
        db (AsyncSession): Database session
        alert (AlertCreateRequest): The alert data to create

    Returns:
        AlertResponse: The created alert response

    Raises:
        DBEntryCreationException: If there's an error creating the alert
        DataBaseException: If there's a database error
    """
    exception = None
    try:
        logger.info("Creating alert with data: %s", alert.model_dump())
        alert_model = Alert(**alert.model_dump())
        db.add(alert_model)
        await db.commit()
        await db.refresh(alert_model)
        logger.info("Successfully created alert with ID: %d", alert_model.id)
        record_alerts_metrics(
            metrics_details=metrics_details,
            status_code=200
        )
        # # Trigger pod deletion if it's a Network-Attack alert with a pod_id
        # if alert_model.alert_type == "Network-Attack" and alert_model.pod_id is not None:
        #     logger.info(
        #         "Network-Attack alert detected for pod_id %s, triggering pod deletion.",
        #         alert_model.pod_id,
        #     )
        #     # Call the delete function (synchronously, since it's not async)
        #     delete_k8s_user_pod(str(alert_model.pod_id), metrics_details=metrics_details)
        return AlertResponse.model_validate(alert_model)
    except IntegrityError as e:
        exception = e
        logger.error("Integrity error while creating alert: %s", str(e))
        await db.rollback()
        raise DBEntryCreationException(
            "Invalid alert data",
            details={"error": str(e)}
        ) from e
    except OperationalError as e:
        exception = e
        logger.error("Database connection error while creating alert: %s", str(e))
        await db.rollback()
        raise DBEntryCreationException(
            "Database operational error while creating alert",
            details={"error": str(e)}
        ) from e
    except SQLAlchemyError as e:
        exception = e
        logger.error("Database error while creating alert: %s", str(e))
        await db.rollback()
        raise DBEntryCreationException(
            "Failed to create alert",
            details={"error": str(e)}
        ) from e
    except Exception as e:
        exception = e
        logger.error("Unexpected error while creating alert: %s", str(e))
        await db.rollback()
        raise e
    finally:
        record_alerts_metrics(
            metrics_details=metrics_details,
            status_code=400,
            exception=exception
        )


async def get_alerts(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        metrics_details: dict = None
) -> Sequence[AlertResponse]:
    """
    Get a list of alerts with pagination.

    Args:
        db (AsyncSession): Database session
        skip (int): Number of records to skip (default: 0)
        limit (int): Maximum number of records to return (default: 100)

    Returns:
        Sequence[AlertResponse]: List of alerts

    Raises:
        DataBaseException: If there's a database error
    """
    exception = None
    try:
        logger.debug("Retrieving alerts with skip=%d, limit=%d", skip, limit)
        query = select(Alert).order_by(Alert.created_at.desc())
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        alerts = result.scalars().all()
        logger.info("Retrieved %d alerts", len(alerts))
        record_alerts_metrics(
            metrics_details=metrics_details,
            status_code=200
        )
        return [AlertResponse.model_validate(alert) for alert in alerts]
    except SQLAlchemyError as e:
        exception = e
        logger.error("Database error while retrieving alerts: %s", str(e))
        raise OrchestrationBaseException(
            "Failed to retrieve alerts",
            details={"error": str(e)}
        ) from e
    except Exception as e:
        exception = e
        logger.error("Unexpected error while retrieving alerts: %s", str(e))
        raise OrchestrationBaseException(
            "An unexpected error occurred while retrieving alerts",
            details={"error": str(e)}
        ) from e
    finally:
        if exception:
            record_alerts_metrics(
                metrics_details=metrics_details,
                status_code=500,
                exception=exception
            )
