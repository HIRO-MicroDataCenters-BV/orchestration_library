"""
Tests for the alerts repository module.
This module tests the creation and retrieval of alerts in the database.
"""

from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError

from app.repositories import alerts as alerts_repo
from app.schemas.alerts_request import AlertResponse, AlertType
from app.tests.utils.mock_objects import mock_alert_create_request_obj, mock_alert_obj
from app.utils.exceptions import DBEntryCreationException, OrchestrationBaseException


@pytest.mark.asyncio
async def test_create_alert_success():
    """Test successful creation of an alert."""
    db = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    alert_data = mock_alert_create_request_obj(
        alert_type=AlertType.ABNORMAL
    )
    alert_obj = mock_alert_obj(
        alert_type=alert_data.alert_type
    )

    with patch("app.repositories.alerts.Alert", return_value=alert_obj):
        created_alert = await alerts_repo.create_alert(db, alert_data)

    db.add.assert_called_once_with(alert_obj)
    db.commit.assert_called_once()
    db.refresh.assert_called_once()

    assert isinstance(created_alert, AlertResponse)
    assert created_alert.alert_type == alert_data.alert_type
    assert created_alert.alert_model is not None
    assert created_alert.alert_description is not None
    assert created_alert.created_at is not None


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
    alert_data = mock_alert_create_request_obj(
        alert_type=AlertType.ABNORMAL
    )
    alert_obj = mock_alert_obj(
        alert_type=alert_data.alert_type
    )

    with patch("app.repositories.alerts.Alert", return_value=alert_obj):
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
    alert_data = mock_alert_create_request_obj(
        alert_type=AlertType.ABNORMAL
    )
    alert_obj = mock_alert_obj(
        alert_type=alert_data.alert_type
    )

    with patch("app.repositories.alerts.Alert", return_value=alert_obj):
        with pytest.raises(Exception):
            await alerts_repo.create_alert(db, alert_data)
    db.rollback.assert_awaited()


@pytest.mark.asyncio
async def test_get_alerts_success():
    """Test successful retrieval of alerts."""
    db = AsyncMock()
    alert_obj1 = mock_alert_obj(
        alert_type=AlertType.ABNORMAL
    )
    alert_obj2 = mock_alert_obj(
        alert_type=AlertType.NETWORK_ATTACK
    )
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
