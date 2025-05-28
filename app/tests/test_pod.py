"""
Tests for DB Pod operations
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import status
from httpx import ASGITransport, AsyncClient

from app.repositories import pod
from app.main import app
from app.models.pod import Pod
from app.schemas.pod import PodCreate, PodUpdate

# ========================= Constants for sample pod data =========================

SAMPLE_POD_OBJECT = Pod(
    **{
        "id": "e2b7c7e6-1a8a-4e3d-9a7e-2f8e2c7b8e1f",
        "name": "test-pod",
        "namespace": "default",
        "is_elastic": False,
        "assigned_node_id": "a3d5f9b2-4c6e-4f1a-9b2e-7c8d1e5a2f3b",
        "workload_request_id": "123e4567-e89b-12d3-a456-426614174000",
        "status": "running",
        "demand_cpu": 0.5,
        "demand_memory": 256,
        "demand_slack_cpu": 0.1,
        "demand_slack_memory": 64,
    }
)

SAMPLE_POD_REQUEST_DATA = {
    "id": "e2b7c7e6-1a8a-4e3d-9a7e-2f8e2c7b8e1f",
    "name": "test-pod",
    "namespace": "default",
    "is_elastic": False,
    "assigned_node_id": "a3d5f9b2-4c6e-4f1a-9b2e-7c8d1e5a2f3b",
    "workload_request_id": "123e4567-e89b-12d3-a456-426614174000",
    "status": "running",
    "demand_cpu": 0.5,
    "demand_memory": 256,
    "demand_slack_cpu": 0.1,
    "demand_slack_memory": 64,
}

SAMPLE_POD_RESPONSE_DATA = {
    "id": "e2b7c7e6-1a8a-4e3d-9a7e-2f8e2c7b8e1f",
    "name": "test-pod",
    "namespace": "default",
    "is_elastic": False,
    "assigned_node_id": "a3d5f9b2-4c6e-4f1a-9b2e-7c8d1e5a2f3b",
    "workload_request_id": "123e4567-e89b-12d3-a456-426614174000",
    "status": "running",
    "demand_cpu": 0.5,
    "demand_memory": 256,
    "demand_slack_cpu": 0.1,
    "demand_slack_memory": 64,
}

SAMPLE_POD_LIST_RESPONSE_DATA = [SAMPLE_POD_RESPONSE_DATA]

SAMPLE_POD_UPDATE_REQUEST_DATA = {"status": "completed"}

SAMPLE_POD_DELETE_RESPONSE_DATA = {
    "message": "Pod with ID e2b7c7e6-1a8a-4e3d-9a7e-2f8e2c7b8e1f has been deleted"
}

# ========================= Tests for pod CRUD functions =========================


@pytest.mark.asyncio
async def test_create_pod():
    """
    Test the create_pod function
    """
    db = AsyncMock()
    pod_data = PodCreate(
        id="e2b7c7e6-1a8a-4e3d-9a7e-2f8e2c7b8e1f",
        name="test-pod",
        namespace="default",
        is_elastic=False,
        assigned_node_id="a3d5f9b2-4c6e-4f1a-9b2e-7c8d1e5a2f3b",
        workload_request_id="123e4567-e89b-12d3-a456-426614174000",
        status="running",
        demand_cpu=0.5,
        demand_memory=256,
        demand_slack_cpu=0.1,
        demand_slack_memory=64,
    )
    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    result = await pod.create_pod(db, pod_data)

    db.add.assert_called_once()
    db.commit.assert_called_once()
    db.refresh.assert_called_once()
    assert isinstance(result, Pod)


@pytest.mark.asyncio
async def test_get_pod():
    """
    Test the get_pod function
    """
    mock_pod = SAMPLE_POD_OBJECT
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = [mock_pod]

    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars

    db = AsyncMock()
    db.execute.return_value = mock_result

    result = await pod.get_pod(
        db,
        pod.PodFilter(
            pod_id="e2b7c7e6-1a8a-4e3d-9a7e-2f8e2c7b8e1f",
            name="test-pod",
            namespace="default",
            is_elastic=False,
            assigned_node_id="a3d5f9b2-4c6e-4f1a-9b2e-7c8d1e5a2f3b",
            workload_request_id="123e4567-e89b-12d3-a456-426614174000",
            status="running",
        ),
    )

    db.execute.assert_called_once()
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0].name == "test-pod"
    assert result[0].status == "running"


@pytest.mark.asyncio
async def test_update_pod():
    """
    Test the update_pod function
    """
    db = AsyncMock()
    mock_pod = MagicMock(spec=Pod, status="pending")
    db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=mock_pod))
    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    updates = PodUpdate(status="completed")
    result = await pod.update_pod(
        db, pod_id="e2b7c7e6-1a8a-4e3d-9a7e-2f8e2c7b8e1f", updates=updates
    )

    db.execute.assert_called_once()
    db.commit.assert_called_once()
    db.refresh.assert_called_once()
    assert result is not None
    assert result.status == "completed"


@pytest.mark.asyncio
async def test_delete_pod():
    """
    Test the delete_pod function
    """
    db = AsyncMock()
    mock_pod = SAMPLE_POD_OBJECT
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_pod
    db.execute = AsyncMock(return_value=mock_result)
    db.delete = AsyncMock()
    db.commit = AsyncMock()

    result = await pod.delete_pod(db, pod_id="e2b7c7e6-1a8a-4e3d-9a7e-2f8e2c7b8e1f")

    db.execute.assert_called_once()
    db.delete.assert_called_once()
    db.commit.assert_called_once()
    assert (
        result["message"]
        == "Pod with ID e2b7c7e6-1a8a-4e3d-9a7e-2f8e2c7b8e1f has been deleted"
    )


# ========================= Tests for pod routes =========================


@pytest.mark.asyncio
@patch("app.repositories.pod.create_pod", new_callable=AsyncMock)
async def test_create_pod_route(mock_create):
    """
    Test the create_pod route
    """
    request_data = SAMPLE_POD_REQUEST_DATA
    response_data = SAMPLE_POD_RESPONSE_DATA

    mock_create.return_value = response_data

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/db_pod/", json=request_data)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == response_data


@pytest.mark.asyncio
@patch("app.repositories.pod.get_pod", new_callable=AsyncMock)
async def test_get_pod_route(mock_get):
    """
    Test the get_pod route
    """
    response_data = SAMPLE_POD_LIST_RESPONSE_DATA
    mock_get.return_value = response_data

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/db_pod/")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == response_data


@pytest.mark.asyncio
@patch("app.repositories.pod.get_pod_by_id", new_callable=AsyncMock)
async def test_get_pod_by_id_route(mock_get):
    """
    Test the get_pod_by_id route
    """
    response_data = SAMPLE_POD_RESPONSE_DATA

    mock_get.return_value = response_data

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/db_pod/e2b7c7e6-1a8a-4e3d-9a7e-2f8e2c7b8e1f")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == response_data


@pytest.mark.asyncio
@patch("app.repositories.pod.update_pod", new_callable=AsyncMock)
async def test_update_pod_route(mock_update):
    """
    Test the update_pod route
    """
    request_data = SAMPLE_POD_UPDATE_REQUEST_DATA
    response_data = SAMPLE_POD_RESPONSE_DATA

    mock_update.return_value = response_data

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.put(
            "/db_pod/e2b7c7e6-1a8a-4e3d-9a7e-2f8e2c7b8e1f", json=request_data
        )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == response_data


@pytest.mark.asyncio
@patch("app.repositories.pod.delete_pod", new_callable=AsyncMock)
async def test_delete_pod_route(mock_delete):
    """
    Test the delete_pod route
    """
    response_data = SAMPLE_POD_DELETE_RESPONSE_DATA
    mock_delete.return_value = response_data

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.delete("/db_pod/e2b7c7e6-1a8a-4e3d-9a7e-2f8e2c7b8e1f")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == response_data
