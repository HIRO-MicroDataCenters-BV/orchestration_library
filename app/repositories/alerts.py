"""
CRUD operations for managing alerts in the database.
"""

from datetime import datetime, timedelta, timezone
import logging
import os
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, OperationalError
from sqlalchemy.ext.asyncio import AsyncSession

from app.metrics.helper import record_alerts_metrics
from app.models.alerts import Alert
from app.schemas.alerts_request import AlertCreateRequest, AlertLevel, AlertResponse
from app.utils.exceptions import DBEntryCreationException, OrchestrationBaseException

logger = logging.getLogger(__name__)


ALERT_CRITICAL_THRESHOLD = int(os.getenv("ALERT_CRITICAL_THRESHOLD", "5"))
ALERT_CRITICAL_THRESHOLD_WINDOW_SECONDS = int(
    os.getenv("ALERT_CRITICAL_THRESHOLD_WINDOW_SECONDS", "60")
)


def is_alert_data_insufficient(alert_obj):
    """
    Check if the alert data is insufficient to create an alert.
    Args:
        alert_obj (AlertCreateRequest): The alert data to check
    """
    if alert_obj is None:
        return True
    fields = [
        alert_obj.pod_id,
        alert_obj.pod_name,
        alert_obj.node_id,
        alert_obj.node_name,
        alert_obj.source_ip,
        alert_obj.destination_ip,
        alert_obj.source_port,
        alert_obj.destination_port,
    ]
    return all(field is None for field in fields)


async def count_recent_similar_alerts(db: AsyncSession, alert_details: dict) -> int:
    """
    Count the number of similar alerts in the last `window_seconds` seconds.

    Args:
        db (AsyncSession): Database session
        alert_details (dict): Details of the alert to match against

    Returns:
        int: Number of similar alerts in the time window
    """
    window_seconds = alert_details.get(
        "window_seconds", ALERT_CRITICAL_THRESHOLD_WINDOW_SECONDS
    )

    alert_window = datetime.now(timezone.utc) - timedelta(seconds=window_seconds)
    count_query = select(Alert.id).where(
        Alert.alert_type == alert_details.get("alert_type"),
        Alert.alert_model == alert_details.get("alert_model"),
        Alert.pod_id == alert_details.get("pod_id"),
        Alert.node_id == alert_details.get("node_id"),
        Alert.pod_name == alert_details.get("pod_name"),
        Alert.node_name == alert_details.get("node_name"),
        Alert.source_ip == alert_details.get("source_ip"),
        Alert.destination_ip == alert_details.get("destination_ip"),
        Alert.source_port == alert_details.get("source_port"),
        Alert.destination_port == alert_details.get("destination_port"),
        Alert.created_at >= alert_window,
    )
    result = await db.execute(count_query)
    return len(result.scalars().all())


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

        if is_alert_data_insufficient(alert):
            logger.error("Ignoring alert with insufficient data: %s", alert)
            raise DBEntryCreationException(
                "Insufficient data to create alert",
                details={"alert_data": alert.model_dump() if alert else None},
            )
        logger.info("Creating alert with data: %s", alert.model_dump())

        recent_count = await count_recent_similar_alerts(
            db,
            alert_details={
                "alert_type": alert.alert_type,
                "alert_model": alert.alert_model,
                "pod_id": alert.pod_id,
                "node_id": alert.node_id,
                "pod_name": alert.pod_name,
                "node_name": alert.node_name,
                "source_ip": alert.source_ip,
                "destination_ip": alert.destination_ip,
                "source_port": alert.source_port,
                "destination_port": alert.destination_port,
                "window_seconds": ALERT_CRITICAL_THRESHOLD_WINDOW_SECONDS,
            },
        )

        alert_model = Alert(**alert.model_dump())
        is_critical = recent_count >= ALERT_CRITICAL_THRESHOLD
        if is_critical:
            alert_model.alert_level = AlertLevel.CRITICAL
        else:
            alert_model.alert_level = AlertLevel.WARNING
        db.add(alert_model)
        await db.commit()
        await db.refresh(alert_model)
        logger.info("Successfully created alert with ID: %d", alert_model.id)
        record_alerts_metrics(metrics_details=metrics_details, status_code=200)

        if is_critical:
            logger.warning(
                "Alert ID %d marked as Critical (count=%d in last %d seconds)",
                alert_model.id,
                recent_count,
                ALERT_CRITICAL_THRESHOLD_WINDOW_SECONDS,
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
            "Invalid alert data", details={"error": str(e)}
        ) from e
    except OperationalError as e:
        exception = e
        logger.error("Database connection error while creating alert: %s", str(e))
        await db.rollback()
        raise DBEntryCreationException(
            "Database operational error while creating alert", details={"error": str(e)}
        ) from e
    except SQLAlchemyError as e:
        exception = e
        logger.error("Database error while creating alert: %s", str(e))
        await db.rollback()
        raise DBEntryCreationException(
            "Failed to create alert", details={"error": str(e)}
        ) from e
    except Exception as e:
        exception = e
        logger.error("Unexpected error while creating alert: %s", str(e))
        await db.rollback()
        raise e
    finally:
        record_alerts_metrics(
            metrics_details=metrics_details, status_code=400, exception=exception
        )


async def get_alerts(
    db: AsyncSession, skip: int = 0, limit: int = 100, metrics_details: dict = None
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
        record_alerts_metrics(metrics_details=metrics_details, status_code=200)
        return [AlertResponse.model_validate(alert) for alert in alerts]
    except SQLAlchemyError as e:
        exception = e
        logger.error("Database error while retrieving alerts: %s", str(e))
        raise OrchestrationBaseException(
            "Failed to retrieve alerts", details={"error": str(e)}
        ) from e
    except Exception as e:
        exception = e
        logger.error("Unexpected error while retrieving alerts: %s", str(e))
        raise OrchestrationBaseException(
            "An unexpected error occurred while retrieving alerts",
            details={"error": str(e)},
        ) from e
    finally:
        if exception:
            record_alerts_metrics(
                metrics_details=metrics_details, status_code=500, exception=exception
            )
