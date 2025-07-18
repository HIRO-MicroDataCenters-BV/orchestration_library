"""Unit tests for workload request decision api."""

from uuid import uuid4
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.tests.utils.mock_objects import mock_mock_workload_request_decision_api

TEST_UUID = str(uuid4())


@pytest.mark.asyncio
@patch(
    "app.api.workload_request_decision_api.create_workload_decision",
    new_callable=AsyncMock,
)
async def test_create_workload_decision(mock_create):
    """Test API endpoint for creating a workload decision."""
    payload = mock_mock_workload_request_decision_api()
    mock_create.return_value = {**payload, "id": TEST_UUID}

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as async_client:
        response = await async_client.post("/workload_request_decision/", json=payload)

    assert response.status_code == 200
    assert response.json()["id"] == TEST_UUID


@pytest.mark.asyncio
@patch(
    "app.api.workload_request_decision_api.get_workload_decision",
    new_callable=AsyncMock,
)
async def test_get_workload_decision(mock_get):
    """Test API endpoint for retrieving a single workload decision."""
    payload = mock_mock_workload_request_decision_api()
    mock_get.return_value = {**payload, "id": TEST_UUID}

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as async_client:
        response = await async_client.get(f"/workload_request_decision/{TEST_UUID}")

    assert response.status_code == 200
    assert response.json()["id"] == TEST_UUID


@pytest.mark.asyncio
@patch(
    "app.api.workload_request_decision_api.get_all_workload_decisions",
    new_callable=AsyncMock,
)
async def test_get_all_workload_decisions(mock_get_all):
    """Test API endpoint for retrieving all workload decisions."""
    payload = mock_mock_workload_request_decision_api()
    mock_get_all.return_value = [{**payload, "id": TEST_UUID}]

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as async_client:
        response = await async_client.get("/workload_request_decision/")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert response.json()[0]["id"] == TEST_UUID


@pytest.mark.asyncio
@patch(
    "app.api.workload_request_decision_api.update_workload_decision",
    new_callable=AsyncMock,
)
async def test_update_workload_decision(mock_update):
    """Test API endpoint for updating a workload decision."""
    update_data = {"pod_name": "updated-pod"}
    mock_update.return_value = update_data

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as async_client:
        response = await async_client.put(
            f"/workload_request_decision/{TEST_UUID}", json=update_data
        )

    assert response.status_code == 200
    assert response.json()["pod_name"] == "updated-pod"


@pytest.mark.asyncio
@patch(
    "app.api.workload_request_decision_api.delete_workload_decision",
    new_callable=AsyncMock,
)
async def test_delete_workload_decision(mock_delete):
    """Test API endpoint for deleting a workload decision."""
    mock_delete.return_value = True

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as async_client:
        response = await async_client.delete(f"/workload_request_decision/{TEST_UUID}")

    assert response.status_code == 200
    assert response.json() is True
