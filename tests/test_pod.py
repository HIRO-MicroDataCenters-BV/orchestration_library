import pytest
from unittest.mock import AsyncMock, patch
from fastapi import status
from httpx import ASGITransport, AsyncClient
from app.schemas import PodCreate, PodUpdate
from app.models import Pod
from app import crud
from app.main import app


# ========================= Tests for pod CRUD functions =========================

@pytest.mark.asyncio
async def test_create_pod():
    db = AsyncMock()
    pod_data = PodCreate(
        name="test-pod",
        namespace="default",
        is_elastic=False,
        assigned_node_id=1,
        status="running"
    )
    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    result = await crud.create_pod(db, pod_data)

    db.add.assert_called_once()
    db.commit.assert_called_once()
    db.refresh.assert_called_once()
    assert isinstance(result, Pod)


@pytest.mark.asyncio
async def test_get_pod():
    db = AsyncMock()
    mock_pod = Pod(
        id=1,
        name="test-pod",
        namespace="default",
        is_elastic=False,
        assigned_node_id=1,
        status="running"
    )
    db.execute = AsyncMock(return_value=AsyncMock(scalars=AsyncMock(all=AsyncMock(return_value=[mock_pod]))))

    result = await crud.get_pod(db)

    db.execute.assert_called_once()
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0].name == "test-pod"
    assert result[0].status == "running"


@pytest.mark.asyncio
async def test_update_pod():
    db = AsyncMock()
    mock_pod = Pod(
        id=1,
        name="test-pod",
        namespace="default",
        is_elastic=False,
        assigned_node_id=1,
        status="running"
    )
    db.execute = AsyncMock(return_value=AsyncMock(scalar_one_or_none=mock_pod))
    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    updates = PodUpdate(status="completed")
    result = await crud.update_pod(db, pod_id=1, updates=updates)

    db.execute.assert_called_once()
    db.commit.assert_called_once()
    db.refresh.assert_called_once()
    assert result is not None
    assert result.status == "completed"


@pytest.mark.asyncio
async def test_delete_pod():
    db = AsyncMock()
    mock_pod = Pod(
        id=1,
        name="test-pod",
        namespace="default",
        is_elastic=False,
        assigned_node_id=1,
        status="running"
    )
    db.execute = AsyncMock(return_value=AsyncMock(scalar_one_or_none=mock_pod))
    db.delete = AsyncMock()
    db.commit = AsyncMock()

    result = await crud.delete_pod(db, pod_id=1)

    db.execute.assert_called_once()
    db.delete.assert_called_once()
    db.commit.assert_called_once()
    assert result["message"] == "Pod with ID 1 has been deleted"


# ========================= Tests for pod routes =========================

@pytest.mark.asyncio
@patch("app.crud.create_pod", new_callable=AsyncMock)
async def test_create_pod_route(mock_create):
    request_data = {
        "name": "test-pod",
        "namespace": "default",
        "is_elastic": False,
        "assigned_node_id": 1,
        "status": "running"
    }
    response_data = {
        "id": 1,
        "name": "test-pod",
        "namespace": "default",
        "is_elastic": False,
        "assigned_node_id": 1,
        "status": "running"
    }

    mock_create.return_value = response_data

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/pod/", json=request_data)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == response_data


@pytest.mark.asyncio
@patch("app.crud.get_pod", new_callable=AsyncMock)
async def test_get_pod_route(mock_get):
    response_data = [
        {
            "id": 1,
            "name": "test-pod",
            "namespace": "default",
            "is_elastic": False,
            "assigned_node_id": 1,
            "status": "running"
        }
    ]

    mock_get.return_value = response_data

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/pod/")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == response_data


@pytest.mark.asyncio
@patch("app.crud.get_pod", new_callable=AsyncMock)
async def test_get_pod_by_id_route(mock_get):
    response_data = {
        "id": 1,
        "name": "test-pod",
        "namespace": "default",
        "is_elastic": False,
        "assigned_node_id": 1,
        "status": "running"
    }

    mock_get.return_value = response_data

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/pod/1")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == response_data


@pytest.mark.asyncio
@patch("app.crud.update_pod", new_callable=AsyncMock)
async def test_update_pod_route(mock_update):
    request_data = {
        "status": "completed"
    }
    response_data = {
        "id": 1,
        "name": "test-pod",
        "namespace": "default",
        "is_elastic": False,
        "assigned_node_id": 1,
        "status": "completed"
    }

    mock_update.return_value = response_data

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.put("/pod/1", json=request_data)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == response_data


@pytest.mark.asyncio
@patch("app.crud.delete_pod", new_callable=AsyncMock)
async def test_delete_pod_route(mock_delete):
    response_data = {"message": "Pod with ID 1 has been deleted"}

    mock_delete.return_value = response_data

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.delete("/pod/1")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == response_data