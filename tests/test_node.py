import pytest
from httpx import AsyncClient
from httpx._transports.asgi import ASGITransport
from fastapi import status
from unittest.mock import AsyncMock, patch, MagicMock
from app.main import app
from app.crud.node import (
    create_node,
    get_nodes,
    update_node,
    delete_node,
)
from app.models import Node
from app.schemas import NodeCreate

# ========================================================================
# ========================= Unit Tests for Node CRUD =====================
# ========================================================================

@pytest.mark.asyncio
@patch("app.crud.node.Node")
async def test_create_node(mock_node_class):
    db = AsyncMock()
    mock_node_obj = MagicMock()
    mock_node_class.return_value = mock_node_obj

    data = NodeCreate(
        name="node-1",
        status="Ready",
        ip_address="192.168.0.1",
        labels={"zone": "us-central1-a"},
    )

    result = await create_node(db, data)

    db.add.assert_called_once_with(mock_node_obj)
    db.commit.assert_awaited_once()
    db.refresh.assert_awaited_once_with(mock_node_obj)
    assert result == mock_node_obj


@pytest.mark.asyncio
async def test_get_nodes_no_filters():
    db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = ["node1", "node2"]
    db.execute.return_value = mock_result

    result = await get_nodes(db)

    db.execute.assert_awaited_once()
    assert result == ["node1", "node2"]


@pytest.mark.asyncio
async def test_get_nodes_with_filters():
    db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = ["filtered-node"]
    db.execute.return_value = mock_result

    result = await get_nodes(db, name="node-1", status="Ready")

    db.execute.assert_awaited_once()
    assert result == ["filtered-node"]


@pytest.mark.asyncio
async def test_update_node():
    db = AsyncMock()
    mock_result = MagicMock()
    mock_node = MagicMock()
    db.execute.return_value = mock_result
    mock_result.scalar_one_or_none.return_value = mock_node

    updates = {"status": "NotReady"}

    result = await update_node(db, 1, updates)

    db.execute.assert_awaited_once()
    assert mock_node.status == "NotReady"
    db.add.assert_called_once_with(mock_node)
    db.commit.assert_awaited_once()
    db.refresh.assert_awaited_once_with(mock_node)
    assert result == mock_node


@pytest.mark.asyncio
async def test_delete_node():
    db = AsyncMock()
    mock_result = MagicMock()
    mock_node = MagicMock()
    db.execute.return_value = mock_result
    mock_result.scalar_one_or_none.return_value = mock_node

    result = await delete_node(db, 1)

    db.execute.assert_awaited_once()
    db.delete.assert_awaited_once_with(mock_node)
    db.commit.assert_awaited_once()
    assert result == {"message": "Node with ID 1 has been deleted"}


@pytest.mark.asyncio
async def test_update_node_not_found():
    db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    db.execute.return_value = mock_result

    result = await update_node(db, 999, {"status": "Unknown"})

    db.execute.assert_awaited_once()
    assert result is None
    db.add.assert_not_called()


@pytest.mark.asyncio
async def test_delete_node_not_found():
    db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    db.execute.return_value = mock_result

    result = await delete_node(db, 999)

    db.execute.assert_awaited_once()
    assert result == {"error": "Node not found"}

# =========================================================================
# ===================== Route-level Tests for Node API ====================
# =========================================================================

@pytest.mark.asyncio
@patch("app.crud.create_node", new_callable=AsyncMock)
async def test_create_node_route(mock_create):
    request_data = {
        "name": "node-1",
        "status": "Ready",
        "ip_address": "192.168.0.1",
        "labels": {"env": "dev"},
    }

    response_data = {
        "id": 1,
        "name": "node-1",
        "status": "Ready",
        "ip_address": "192.168.0.1",
        "labels": {"env": "dev"},
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z",
    }

    mock_create.return_value = response_data

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/node/", json=request_data)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == response_data


@pytest.mark.asyncio
@patch("app.crud.update_node", new_callable=AsyncMock)
async def test_update_node_route(mock_update):
    request_data = {"status": "NotReady"}

    response_data = {
        "id": 1,
        "name": "node-1",
        "status": "NotReady",
        "ip_address": "192.168.0.1",
        "labels": {"env": "dev"},
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T01:00:00Z",
    }

    mock_update.return_value = response_data

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.put("/node/1", json=request_data)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == response_data


@pytest.mark.asyncio
@patch("app.crud.delete_node", new_callable=AsyncMock)
async def test_delete_node_route(mock_delete):
    response_data = {"message": "Node with ID 1 has been deleted"}
    mock_delete.return_value = response_data

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.delete("/node/1")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == response_data


@pytest.mark.asyncio
@patch("app.crud.get_nodes", new_callable=AsyncMock)
async def test_get_all_nodes_route(mock_get):
    response_data = [{
        "id": 1,
        "name": "node-1",
        "status": "Ready",
        "ip_address": "192.168.0.1",
        "labels": {"env": "prod"},
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z",
    }]

    mock_get.return_value = response_data

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/node/")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == response_data


@pytest.mark.asyncio
@patch("app.crud.get_nodes", new_callable=AsyncMock)
async def test_get_node_by_id_route(mock_get):
    response_data = {
        "id": 1,
        "name": "node-1",
        "status": "Ready",
        "ip_address": "192.168.0.1",
        "labels": {"env": "prod"},
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z",
    }

    mock_get.return_value = response_data

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/node/1")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == response_data
