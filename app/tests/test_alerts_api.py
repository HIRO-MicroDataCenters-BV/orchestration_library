"""Tests for the alerts API endpoints in the FastAPI application.
This module tests the creation and retrieval of alerts through the API.
"""

import pytest
from httpx import ASGITransport, AsyncClient
from fastapi import status
from unittest.mock import AsyncMock, patch

from app.main import app
from app.tests.utils.mock_objects import (
    mock_alert_create_request_data,
    mock_alert_response_obj,
)


@pytest.mark.asyncio
@patch("app.repositories.alerts.create_alert", new_callable=AsyncMock)
async def test_create_alert_success(mock_create_alert):
    """Test successful creation of an alert through the API."""
    alert_create_data = mock_alert_create_request_data()
    alert_response_obj = mock_alert_response_obj(**alert_create_data)

    mock_create_alert.return_value = alert_response_obj

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/alerts/", json=alert_create_data)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["alert_model"] == alert_response_obj.alert_model
    assert response.json()["created_at"] is not None


@pytest.mark.asyncio
@patch("app.repositories.alerts.get_alerts", new_callable=AsyncMock)
async def test_read_alerts_success(mock_get_alerts):
    """Test successful retrieval of alerts."""
    alert_create_data = mock_alert_create_request_data()
    alert_response_obj = mock_alert_response_obj(**alert_create_data)

    mock_get_alerts.return_value = [alert_response_obj]

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/alerts/")

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)
    assert response.json()[0]["alert_model"] == alert_response_obj.alert_model
