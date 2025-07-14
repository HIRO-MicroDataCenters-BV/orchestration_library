"""Tests for the alerts API endpoints in the FastAPI application.
This module tests the creation and retrieval of alerts through the API.
"""
import pytest
from httpx import AsyncClient
from fastapi import status
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from app.main import app
from app.schemas.alerts_request import AlertCreateRequest, AlertType, AlertResponse
from app.tests.utils.mock_objects import mock_alert_data_dict

@pytest.fixture
def alert_create_data():
    return {
        "alert_type": AlertType.ABNORMAL,
        "alert_model": "TestModel",
        "alert_description": "Test alert",
        "pod_id": str(uuid4()),
        "node_id": str(uuid4()),
    }

@pytest.fixture
def alert_response_data(alert_create_data):
    return {
        "id": 1,
        "alert_type": alert_create_data["alert_type"],
        "alert_model": alert_create_data["alert_model"],
        "alert_description": alert_create_data["alert_description"],
        "pod_id": alert_create_data["pod_id"],
        "node_id": alert_create_data["node_id"],
        "created_at": "2024-07-15T12:00:00Z",
    }

@pytest.mark.asyncio
@patch("app.repositories.alerts.create_alert", new_callable=AsyncMock)
async def test_create_alert_success(mock_create_alert, alert_create_data, alert_response_data):
    alert_create_data = mock_alert_data_dict()
    alert_response_data = moc
    mock_create_alert.return_value = AlertResponse(**alert_response_data)
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/alerts/", json=alert_create_data)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["alert_model"] == alert_response_data["alert_model"]

@pytest.mark.asyncio
@patch("app.repositories.alerts.create_alert", new_callable=AsyncMock)
async def test_create_alert_db_error(mock_create_alert, alert_create_data):
    mock_create_alert.side_effect = Exception("db error")
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/alerts/", json=alert_create_data)
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

@pytest.mark.asyncio
@patch("app.repositories.alerts.get_alerts", new_callable=AsyncMock)
async def test_read_alerts_success(mock_get_alerts, alert_response_data):
    mock_get_alerts.return_value = [AlertResponse(**alert_response_data)]
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/alerts/")
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)
    assert response.json()[0]["alert_model"] == alert_response_data["alert_model"]

@pytest.mark.asyncio
@patch("app.repositories.alerts.get_alerts", new_callable=AsyncMock)
async def test_read_alerts_db_error(mock_get_alerts):
    mock_get_alerts.side_effect = Exception("db error")
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/alerts/")
    assert