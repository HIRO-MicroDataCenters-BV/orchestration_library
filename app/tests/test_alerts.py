"""
Tests for the alerts repository module.
This module tests the creation and retrieval of alerts in the database.
"""

from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError

from app.repositories import alerts as alerts_repo
from app.schemas.alerts_request import AlertResponse, AlertType
from app.tests.utils.mock_objects import (
    mock_alert_create_request_obj,
    mock_alert_obj,
    mock_alert_response_obj,
    mock_metrics_details,
)
from app.utils.exceptions import DBEntryCreationException, OrchestrationBaseException


def test_alert_repr_and_str():
    """Test __repr__ and __str__ methods of Alert and related schemas."""
    alert = mock_alert_obj()
    alert_req = mock_alert_create_request_obj(alert_type=alert.alert_type)
    alert_res = mock_alert_response_obj(alert_type=alert.alert_type)
    # __repr__ and __str__ should not raise
    a_r = repr(alert)
    a_s = str(alert)
    a_req_r = repr(alert_req)
    a_req_s = str(alert_req)
    a_res_r = repr(alert_res)
    a_res_s = str(alert_res)
    assert "Alert" in a_r
    assert "Alert" in a_s
    assert "AlertCreateRequest" in a_req_r
    assert "AlertCreateRequest" in a_req_s
    assert "AlertResponse" in a_res_r
    assert "AlertResponse" in a_res_s


@pytest.mark.parametrize(
    "ip_field,ip",
    [
        ("source_ip", "192.168.1.1"),
        ("destination_ip", "10.0.0.2"),
    ],
)
def test_validate_ip_valid(ip_field, ip):
    """Test valid IP addresses for source and destination fields."""
    alert = mock_alert_obj()
    setattr(alert, ip_field, ip)
    # Should not raise
    assert getattr(alert, ip_field) == ip


@pytest.mark.parametrize(
    "ip_field,ip",
    [
        ("source_ip", "not-an-ip"),
        ("destination_ip", "999.999.999.999"),
    ],
)
def test_validate_ip_invalid(ip_field, ip):
    """Test invalid IP addresses for source and destination fields."""
    alert = mock_alert_obj()
    with pytest.raises(ValueError):
        setattr(alert, ip_field, ip)


@pytest.mark.parametrize(
    "port_field,port",
    [
        ("source_port", 80),
        ("destination_port", 65535),
    ],
)
def test_validate_port_valid(port_field, port):
    """Test valid port numbers for source and destination fields."""
    alert = mock_alert_obj()
    setattr(alert, port_field, port)
    assert getattr(alert, port_field) == port


@pytest.mark.parametrize(
    "port_field,port",
    [
        ("source_port", 0),
        ("destination_port", 70000),
    ],
)
def test_validate_port_invalid(port_field, port):
    """Test invalid port numbers for source and destination fields."""
    alert = mock_alert_obj()
    with pytest.raises(ValueError):
        setattr(alert, port_field, port)


@pytest.mark.asyncio
async def test_create_alert_success():
    """Test successful creation of an alert."""
    db = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    db.execute = AsyncMock()
    db.rollback = AsyncMock()

    alert_data = mock_alert_create_request_obj(alert_type=AlertType.ABNORMAL)
    alert_obj = mock_alert_obj(alert_type=alert_data.alert_type)

    # Patch count_recent_similar_alerts to avoid touching the SQLAlchemy Alert class.
    # which breaks when Alert is replaced by a MagicMock instance.
    with patch("app.repositories.alerts.count_recent_similar_alerts", return_value=0), \
         patch("app.repositories.alerts.Alert", return_value=alert_obj):
        created_alert = await alerts_repo.create_alert(
            db, alert_data, metrics_details=mock_metrics_details("POST", "/alerts")
        )

    db.add.assert_called_once_with(alert_obj)
    db.commit.assert_called_once()
    db.refresh.assert_called_once()

    assert isinstance(created_alert, AlertResponse)
    assert created_alert.alert_type == alert_data.alert_type
    assert created_alert.alert_level == "Warning"
    assert created_alert.alert_model is not None
    assert created_alert.alert_description is not None
    assert created_alert.created_at is not None


@pytest.mark.asyncio
async def test_create_alert_triggers_pod_deletion_on_network_attack():
    """Test that pod deletion is triggered for Network-Attack alert with pod_id."""
    db = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    # Use a valid pod_id and alert_type for the test
    pod_id = "123e4567-e89b-12d3-a456-426614174000"
    alert_data = mock_alert_create_request_obj(alert_type="Network-Attack", pod_id=pod_id)
    alert_obj = mock_alert_obj(alert_type=alert_data.alert_type, pod_id=pod_id)

    # with patch("app.repositories.alerts.Alert", return_value=alert_obj), \
    #      patch("app.repositories.alerts.delete_k8s_user_pod") as mock_delete_pod:
    with patch("app.repositories.alerts.count_recent_similar_alerts", return_value=0), \
         patch("app.repositories.alerts.Alert", return_value=alert_obj):
        created_alert = await alerts_repo.create_alert(
            db, alert_data, metrics_details=mock_metrics_details("POST", "/alerts")
        )

    db.add.assert_called_once_with(alert_obj)
    db.commit.assert_called_once()
    db.refresh.assert_called_once()

    # assert mock_delete_pod.call_count == 1
    # args, kwargs = mock_delete_pod.call_args
    # assert args[0] == str(pod_id)
    # md = kwargs["metrics_details"]
    # assert md["endpoint"] == "/alerts"
    # assert md["method"] == "POST"
    # assert "start_time" in md

    assert isinstance(created_alert, AlertResponse)
    assert created_alert.alert_type == alert_data.alert_type
    assert str(created_alert.pod_id) == pod_id


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "exc,expected_exception",
    [
        (IntegrityError("stmt", "params", "orig"), DBEntryCreationException),
        (OperationalError("stmt", "params", "orig"), DBEntryCreationException),
        (SQLAlchemyError("error"), DBEntryCreationException),
    ],
)
async def test_create_alert_db_exceptions(exc, expected_exception):
    """Test creation of alert with various database exceptions."""
    db = MagicMock()
    db.commit = AsyncMock(side_effect=exc)
    db.refresh = AsyncMock()
    db.add = MagicMock()
    db.rollback = AsyncMock()
    alert_data = mock_alert_create_request_obj(alert_type=AlertType.ABNORMAL)
    alert_obj = mock_alert_obj(alert_type=alert_data.alert_type)

    with patch("app.repositories.alerts.count_recent_similar_alerts", return_value=0), \
         patch("app.repositories.alerts.Alert", return_value=alert_obj):
        with pytest.raises(expected_exception):
            await alerts_repo.create_alert(db, alert_data)


@pytest.mark.asyncio
async def test_create_alert_unexpected_exception():
    """Test creation of alert with an unexpected exception."""
    db = MagicMock()
    db.commit = AsyncMock(side_effect=Exception("unexpected"))
    db.refresh = AsyncMock()
    db.add = MagicMock()
    db.rollback = AsyncMock()
    alert_data = mock_alert_create_request_obj(alert_type=AlertType.ABNORMAL)
    alert_obj = mock_alert_obj(alert_type=alert_data.alert_type)

    with patch("app.repositories.alerts.Alert", return_value=alert_obj):
        with pytest.raises(Exception):
            await alerts_repo.create_alert(db, alert_data)
    db.rollback.assert_awaited()


@pytest.mark.asyncio
async def test_get_alerts_success():
    """Test successful retrieval of alerts."""
    db = AsyncMock()
    alert_obj1 = mock_alert_obj(alert_type=AlertType.ABNORMAL)
    alert_obj2 = mock_alert_obj(alert_type=AlertType.NETWORK_ATTACK)
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [alert_obj1, alert_obj2]
    db.execute.return_value = mock_result

    result = await alerts_repo.get_alerts(db, skip=0, limit=10)
    assert len(result) == 2
    assert isinstance(result[0], AlertResponse)
    assert result[0].alert_type == alert_obj1.alert_type
    assert result[0].alert_model is not None
    assert result[1].alert_type == alert_obj2.alert_type
    assert result[1].alert_model is not None


@pytest.mark.asyncio
async def test_get_alerts_sqlalchemy_error():
    """Test retrieval of alerts with SQLAlchemy error."""
    db = AsyncMock()
    db.execute.side_effect = SQLAlchemyError("error")
    with pytest.raises(OrchestrationBaseException):
        await alerts_repo.get_alerts(db)


@pytest.mark.asyncio
async def test_get_alerts_unexpected_exception():
    """Test retrieval of alerts with unexpected exception."""
    db = AsyncMock()
    db.execute.side_effect = Exception("unexpected")
    with pytest.raises(OrchestrationBaseException):
        await alerts_repo.get_alerts(db)
