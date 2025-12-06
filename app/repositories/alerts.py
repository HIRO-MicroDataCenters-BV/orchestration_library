"""
CRUD operations for managing alerts in the database.
"""

from datetime import datetime, timedelta, timezone
from http import HTTPStatus
import logging
import os
import time
from typing import Sequence
from sqlalchemy import Boolean, select
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, OperationalError
from sqlalchemy.ext.asyncio import AsyncSession

from app.metrics.helper import record_alerts_metrics
from app.models.alerts import Alert
from app.repositories.k8s.k8s_common import get_k8s_apps_v1_client
from app.repositories.k8s.k8s_pod import (
    delete_pod_via_alert_action_service,
    get_k8s_pod_containrers_resources,
    get_k8s_pod_obj,
    get_pod_and_controller,
    resolve_controller,
    scaleup_pod_via_alert_action_service,
    update_pod_resources_via_alert_action_service,
)
from app.schemas.alerts_request import AlertCreateRequest, AlertLevel, AlertResponse
from app.utils.constants import (
    CPU_RESOURCE_UPDATE_ALERTS,
    MEMORY_RESOURCE_UPDATE_ALERTS,
    POD_REDEPLOY_ALERTS,
)
from app.utils.exceptions import (
    DBEntryCreationException,
    OrchestrationBaseException,
    AlertActionException,
)

logger = logging.getLogger(__name__)


ALERT_CRITICAL_THRESHOLD = int(os.getenv("ALERT_CRITICAL_THRESHOLD", "5"))
ALERT_CRITICAL_THRESHOLD_WINDOW_SECONDS = int(
    os.getenv("ALERT_CRITICAL_THRESHOLD_WINDOW_SECONDS", "60")
)
ALERT_ACTION_TRIGGER_SERVICE_URL = os.getenv(
    "ALERT_ACTION_TRIGGER_SERVICE_URL", "http://wam-app:3030"
)


def normalize_description(alert_model: Alert):
    """Return (description, desc_lower, alert_id)."""
    description = (alert_model.alert_description or "").strip()
    return description, description.lower(), getattr(alert_model, "id", None)


def handle_resource_update(alert_model: Alert, resource_type: str) -> bool:
    """
    Perform resource update action (cpu or memory); return True if executed.
    resource_type: "cpu" or "memory"
    """
    if resource_type not in {"cpu", "memory"}:
        logger.error(
            "Unsupported resource_type '%s' (alert ID %s)",
            resource_type,
            getattr(alert_model, "id", None),
        )
        return False

    pod, controller_owner = get_pod_and_controller(
        pod_id=alert_model.pod_id, pod_name=alert_model.pod_name
    )
    if not pod or not controller_owner:
        logger.error(
            "%s update aborted: pod/controller not found (alert ID %s, pod_id=%s, pod_name=%s)",
            resource_type.upper(),
            getattr(alert_model, "id", None),
            alert_model.pod_id,
            alert_model.pod_name,
        )
        return False

    namespace = pod.metadata.namespace
    apps_v1 = get_k8s_apps_v1_client()
    replicas, kind, name = resolve_controller(apps_v1, controller_owner, namespace)
    containers_resources = get_k8s_pod_containrers_resources(pod)

    update_pod_resources_via_alert_action_service(
        controller_details={"kind": kind, "name": name, "replicas": replicas},
        pod_details={"name": pod.metadata.name, "namespace": namespace},
        containers_resources=containers_resources,
        service_url=ALERT_ACTION_TRIGGER_SERVICE_URL,
        update_resource_type=resource_type,
    )

    logger.info(
        "%s resource update action sent (alert ID %s, controller=%s/%s)",
        resource_type.upper(),
        getattr(alert_model, "id", None),
        kind,
        name,
    )
    return True


def handle_cpu_update(alert_model: Alert) -> bool:
    """Perform CPU resource update action; return True if executed."""
    return handle_resource_update(alert_model, resource_type="cpu")


def handle_memory_update(alert_model: Alert) -> bool:
    """Perform Memory resource update action; return True if executed."""
    return handle_resource_update(alert_model, resource_type="memory")


def handle_pod_redeploy(alert_model: Alert) -> bool:
    """Perform pod delete action; return True if executed."""
    pod = get_k8s_pod_obj(pod_id=alert_model.pod_id, pod_name=alert_model.pod_name)
    if not pod:
        logger.error(
            "Pod redeploy aborted: pod not found (alert ID %s, pod_id=%s, pod_name=%s)",
            getattr(alert_model, "id", None),
            alert_model.pod_id,
            alert_model.pod_name,
        )
        return False
    pod_name = pod.metadata.name
    namespace = pod.metadata.namespace
    node_name = getattr(pod.spec, "node_name", None)
    action_response = scaleup_pod_via_alert_action_service(
        pod_name=pod_name,
        namespace=namespace,
        node_name=node_name,
        service_url=ALERT_ACTION_TRIGGER_SERVICE_URL,
    )
    logger.info(
        "Pod scale-up action sent (alert ID %s, pod=%s)",
        getattr(alert_model, "id", None),
        pod.metadata.name,
    )
    if action_response.status_code != HTTPStatus.OK:
        logger.error(
            "Pod scale-up action failed (alert ID %s, pod=%s, response=%s)",
            getattr(alert_model, "id", None),
            pod.metadata.name,
            action_response,
        )
        return False
    logger.info("Waiting 3 seconds before deleting pod to allow scale-up...")
    time.sleep(3)
    action_response = delete_pod_via_alert_action_service(
        pod_name=pod_name,
        namespace=namespace,
        node_name=node_name,
        service_url=ALERT_ACTION_TRIGGER_SERVICE_URL,
    )
    logger.info(
        "Pod delete action sent (alert ID %s, pod=%s)",
        getattr(alert_model, "id", None),
        pod.metadata.name,
    )
    if action_response.status_code != HTTPStatus.OK:
        logger.error(
            "Pod delete action failed (alert ID %s, pod=%s, response=%s)",
            getattr(alert_model, "id", None),
            pod.metadata.name,
            action_response,
        )
        return False

    return True


def handle_post_create_alert_actions(alert_model: Alert) -> None:
    """
    Execute post-create actions based on alert description.
    Silent if prerequisites missing. Raises AlertActionException for unexpected failures.
    """
    try:
        description, desc_lower, alert_id = normalize_description(alert_model)
        performed_action = False

        if not description:
            logger.debug(
                "Skipping post-create actions: empty description (alert ID %s)",
                alert_id,
            )
        else:
            logger.warning(
                "Alert ID %s triggered post-create actions: %s",
                alert_id,
                description,
            )

            is_cpu = desc_lower in CPU_RESOURCE_UPDATE_ALERTS
            is_memory = desc_lower in MEMORY_RESOURCE_UPDATE_ALERTS
            is_redeploy = desc_lower in POD_REDEPLOY_ALERTS

            if not (is_cpu or is_memory or is_redeploy):
                logger.debug(
                    "No mapped post-create action (alert ID %s, description=%s)",
                    alert_id,
                    description,
                )
            elif not (alert_model.pod_id or alert_model.pod_name):
                logger.error(
                    "Action requires pod reference; missing pod_id/pod_name (alert ID %s)",
                    alert_id,
                )
            else:
                if is_cpu:
                    performed_action |= handle_cpu_update(alert_model)
                if is_memory:
                    performed_action |= handle_memory_update(alert_model)
                if is_redeploy:
                    performed_action |= handle_pod_redeploy(alert_model)

        if not performed_action:
            logger.debug("No post-create action executed (alert ID %s)", alert_id)

    except AlertActionException:
        # Propagate explicit action failures
        raise
    except Exception as e:
        alert_id = getattr(alert_model, "id", None)
        logger.error(
            "Unexpected error in post-create actions for alert ID %s: %s",
            alert_id,
            e,
        )
        raise AlertActionException(
            "Failed to handle post-create alert actions",
            details={"error": str(e), "alert_id": alert_id},
        ) from e


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
    field_map = {
        Alert.alert_type: alert_details.get("alert_type"),
        Alert.alert_model: alert_details.get("alert_model"),
        Alert.pod_id: alert_details.get("pod_id"),
        Alert.node_id: alert_details.get("node_id"),
        Alert.pod_name: alert_details.get("pod_name"),
        Alert.node_name: alert_details.get("node_name"),
        Alert.source_ip: alert_details.get("source_ip"),
        Alert.destination_ip: alert_details.get("destination_ip"),
        Alert.source_port: alert_details.get("source_port"),
        Alert.destination_port: alert_details.get("destination_port"),
    }

    conditions = []
    for column, value in field_map.items():
        if value is None:
            conditions.append(column.is_(None))
        else:
            conditions.append(column == value)

    conditions.append(Alert.created_at >= alert_window)

    count_query = select(Alert.id).where(*conditions)
    result = await db.execute(count_query)
    return len(result.scalars().all())


async def validate_alert_data(alert: AlertCreateRequest):
    """
    Validate the alert data before creation.
    Args:
        alert (AlertCreateRequest): The alert data to validate
    Raises:
        DBEntryCreationException: If the alert data is insufficient
    """
    if is_alert_data_insufficient(alert):
        logger.error("Ignoring alert with insufficient data: %s", alert)
        raise DBEntryCreationException(
            "Insufficient data to create alert",
            details={"alert_data": alert.model_dump() if alert else None},
        )
    logger.info("Creating alert with data: %s", alert.model_dump())


async def get_recent_count(db: AsyncSession, alert: AlertCreateRequest):
    """
    Get the count of recent similar alerts within the critical threshold window.
    Args:
        db (AsyncSession): Database session
        alert (AlertCreateRequest): The alert data to check against
    """
    return await count_recent_similar_alerts(
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


async def persist_alert(db: AsyncSession, alert_model: Alert):
    """
    Persist the alert model to the database.

    Args:
        db (AsyncSession): Database session
        alert_model (Alert): The alert model to persist
    """
    db.add(alert_model)
    await db.commit()
    await db.refresh(alert_model)
    logger.info("Successfully created alert with ID: %d", alert_model.id)


def set_alert_level(alert_model: Alert, recent_count: int):
    """
    Set the alert level based on the recent count of similar alerts.

    Args:
        alert_model (Alert): The alert model to update
        recent_count (int): The count of recent similar alerts

    Returns:
        bool: True if the alert is critical, False otherwise
    """
    is_critical = recent_count >= ALERT_CRITICAL_THRESHOLD
    alert_model.alert_level = AlertLevel.CRITICAL if is_critical else AlertLevel.WARNING
    return is_critical


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
    post_actions_exception = None
    try:
        await validate_alert_data(alert)
        recent_count = await get_recent_count(db, alert)
        alert_model = Alert(**alert.model_dump())
        is_critical = set_alert_level(alert_model, recent_count)
        await persist_alert(db, alert_model)
        record_alerts_metrics(metrics_details=metrics_details, status_code=200)

        if is_critical:
            logger.warning(
                "Alert ID %d marked as Critical (count=%d in last %d seconds)",
                alert_model.id,
                recent_count,
                ALERT_CRITICAL_THRESHOLD_WINDOW_SECONDS,
            )
        if recent_count > 0:
            logger.info(
                "Post-create alert action already executed for the first occurrence; "
                "this is occurrence #%d. Skipping post-create alert action.",
                recent_count + 1,
            )
        else:
            # Post-create actions: do NOT raise if they fail (alert already persisted)
            try:
                logger.info(
                    "Executing post-create alert actions for alert ID %d",
                    alert_model.id,
                )
                handle_post_create_alert_actions(alert_model)
            except AlertActionException as act_exc:
                post_actions_exception = act_exc
                logger.error(
                    "Post-create alert actions failed for alert ID %d: %s",
                    alert_model.id,
                    str(act_exc),
                )
        record_alerts_metrics(
            metrics_details=metrics_details,
            status_code=200,
            exception=post_actions_exception if post_actions_exception else None,
        )
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
        raise
    finally:
        if exception:
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


async def perform_action_on_alert(
    db: AsyncSession, action_id: int, metrics_details: dict = None
) -> Boolean:
    """
    Perform an action on an alert (e.g., acknowledge, resolve).

    Args:
        db (AsyncSession): Database session
        action_id (int): The ID of the alert to perform action on
        metrics_details (dict): Metrics details for recording

    Returns:
        Boolean: True if the action was performed successfully, False otherwise

    Raises:
        DataBaseException: If there's a database error
    """
    exception = None
    try:
        logger.debug("Performing action on alert with ID=%d", action_id)
        query = select(Alert).where(Alert.id == action_id)
        result = await db.execute(query)
        alert = result.scalars().first()
        if not alert:
            logger.error("Alert with ID=%d not found", action_id)
            raise AlertActionException(
                f"Alert with ID {action_id} not found",
                details={"alert_id": action_id},
            )
        handle_post_create_alert_actions(alert)
        record_alerts_metrics(metrics_details=metrics_details, status_code=200)
        logger.info("Performed action on alert with ID=%d", alert.id)
        return True
    except SQLAlchemyError as e:
        exception = e
        logger.error("Database error while performing action on alert: %s", str(e))
        raise AlertActionException(
            "Failed to perform action on alert", details={"error": str(e)}
        ) from e
    except Exception as e:
        exception = e
        logger.error("Unexpected error while performing action on alert: %s", str(e))
        raise AlertActionException(
            "An unexpected error occurred while performing action on alert",
            details={"error": str(e)},
        ) from e
    finally:
        if exception:
            record_alerts_metrics(
                metrics_details=metrics_details, status_code=500, exception=exception
            )
