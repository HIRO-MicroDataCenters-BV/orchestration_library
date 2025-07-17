import pytest
from uuid import uuid4
from datetime import datetime, timezone
from httpx import AsyncClient
from httpx import ASGITransport
from unittest.mock import AsyncMock, patch

from app.main import app
from app.utils.constants import POD_PARENT_TYPE_ENUM

TEST_UUID = str(uuid4())
TEST_DATE = datetime.now(timezone.utc)

TEST_CREATE_PAYLOAD = {
    "pod_id": str(uuid4()),
    "pod_name": "test-pod",
    "namespace": "default",
    "node_id": str(uuid4()),
    "node_name": "node-1",
    "is_elastic": True,
    "queue_name": "queue-A",
    "demand_cpu": 1.0,
    "demand_memory": 512.0,
    "demand_slack_cpu": 0.5,
    "demand_slack_memory": 128.0,
    "is_decision_status": True,
    "pod_parent_id": str(uuid4()),
    "pod_parent_name": "controller-1",
    "pod_parent_kind": POD_PARENT_TYPE_ENUM[0],
    "created_at": TEST_DATE.isoformat(),
    "deleted_at": None,
}


@pytest.mark.asyncio
@patch(
    "app.api.workload_request_decision_api.create_workload_decision",
    new_callable=AsyncMock,
)
async def test_create_workload_decision(mock_create):
    mock_create.return_value = {**TEST_CREATE_PAYLOAD, "id": TEST_UUID}

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            "/workload_request_decision/", json=TEST_CREATE_PAYLOAD
        )

    assert response.status_code == 200
    assert response.json()["id"] == TEST_UUID


@pytest.mark.asyncio
@patch(
    "app.api.workload_request_decision_api.get_workload_decision",
    new_callable=AsyncMock,
)
async def test_get_workload_decision(mock_get):
    mock_get.return_value = {**TEST_CREATE_PAYLOAD, "id": TEST_UUID}

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get(f"/workload_request_decision/{TEST_UUID}")

    assert response.status_code == 200
    assert response.json()["id"] == TEST_UUID


@pytest.mark.asyncio
@patch(
    "app.api.workload_request_decision_api.get_all_workload_decisions",
    new_callable=AsyncMock,
)
async def test_get_all_workload_decisions(mock_get_all):
    mock_get_all.return_value = [{**TEST_CREATE_PAYLOAD, "id": TEST_UUID}]

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/workload_request_decision/")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert response.json()[0]["id"] == TEST_UUID


@pytest.mark.asyncio
@patch(
    "app.api.workload_request_decision_api.update_workload_decision",
    new_callable=AsyncMock,
)
async def test_update_workload_decision(mock_update):
    update_data = {"pod_name": "updated-pod"}
    mock_update.return_value = update_data

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.put(
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
    mock_delete.return_value = True

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.delete(f"/workload_request_decision/{TEST_UUID}")

    assert response.status_code == 200
    assert response.json() is True
