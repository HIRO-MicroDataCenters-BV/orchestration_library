import pytest
from unittest.mock import MagicMock
from app.crud.node import create_node, get_nodes, update_node, delete_node
from app.schemas import NodeCreate
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from httpx._transports.asgi import ASGITransport


import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock
from app.main import app
from app.schemas import NodeCreate


from sqlalchemy.orm import Session
from app.models import Node

# ===========================================================================
# ========================= Tests for node CRUD functions =========================
# ===========================================================================


@pytest.mark.asyncio
async def test_create_node_crud():
    db = AsyncMock()
    data = NodeCreate(
        name="node-1",
        status="active",
        cpu_capacity=4.0,
        memory_capacity=8192.0,
        ip_address="192.168.1.1",
        location="loc1",
    )

    node_instance = MagicMock()
    db.add = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    with patch("app.crud.node.Node", return_value=node_instance):
        result = await create_node(db, data)

    db.add.assert_called_once_with(node_instance)
    db.commit.assert_awaited_once()
    db.refresh.assert_awaited_once_with(node_instance)
    assert result == node_instance


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "node_id, expected", [(None, ["node1", "node2"]), (1, ["filtered-node"])]
)
async def test_get_nodes_crud(node_id, expected):
    db = AsyncMock()
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = expected
    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars
    db.execute = AsyncMock(return_value=mock_result)

    result = await get_nodes(db, node_id=node_id)
    assert result == expected


@pytest.mark.asyncio
async def test_update_node_crud():
    db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = {"id": 1, "name": "updated-node"}

    db.execute = AsyncMock(side_effect=[None, mock_result])
    db.commit = AsyncMock()

    updates = {"name": "updated-node"}
    result = await update_node(db, node_id=1, updates=updates)

    assert result == {"id": 1, "name": "updated-node"}
    assert db.execute.await_count == 2
    db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_node_crud():
    db = AsyncMock()
    db.execute = AsyncMock()
    db.commit = AsyncMock()

    result = await delete_node(db, node_id=1)

    db.execute.assert_awaited_once()
    db.commit.assert_awaited_once()
    assert result == {"deleted_id": 1}


# =====================================================================================
# ========================= Below tests are for the node routes =========================
# =====================================================================================


import pytest
from unittest.mock import AsyncMock, patch
from fastapi import status
from httpx import AsyncClient
from app.main import app
from app.schemas import NodeCreate, NodeResponse


@pytest.mark.asyncio
@patch("app.crud.node.create_node", new_callable=AsyncMock)
async def test_create_node(mock_create_node):
    # Define the request and expected response data
    request_data = NodeCreate(
        name="test-node",
        status="active",
        cpu_capacity=4.0,
        memory_capacity=8192.0,
        current_cpu_assignment=1.0,
        current_memory_assignment=1024.0,
        current_cpu_utilization=0.5,
        current_memory_utilization=512.0,
    )

    response_data = NodeResponse(
        id=1,
        name="test-node",
        status="active",
        cpu_capacity=4.0,
        memory_capacity=8192.0,
        current_cpu_assignment=1.0,
        current_memory_assignment=1024.0,
        current_cpu_utilization=0.5,
        current_memory_utilization=512.0,
        ip_address="192.168.1.1",  # Assuming this is added to response
        location="datacenter-1",  # Assuming this is added to response
    )

    # Mock the `create_node` function to return the expected data
    mock_create_node.return_value = response_data
    transport = ASGITransport(app=app)
    # Set up the test client
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/node/", json=request_data.dict())

    # Assertions
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == response_data.dict()


@pytest.mark.asyncio
@patch("app.crud.node.get_nodes", new_callable=AsyncMock)
async def test_get_nodes(mock_get_nodes):
    # Sample node data to be returned
    nodes = [
        {
            "id": 1,
            "name": "test-node-1",
            "status": "active",
            "cpu_capacity": 4.0,
            "memory_capacity": 8192.0,
            "current_cpu_assignment": 1.0,
            "current_memory_assignment": 1024.0,
            "current_cpu_utilization": 0.5,
            "current_memory_utilization": 512.0,
            "ip_address": "192.168.1.1",
            "location": "datacenter-1",
        },
        {
            "id": 2,
            "name": "test-node-2",
            "status": "inactive",
            "cpu_capacity": 8.0,
            "memory_capacity": 16384.0,
            "current_cpu_assignment": 2.0,
            "current_memory_assignment": 2048.0,
            "current_cpu_utilization": 0.25,
            "current_memory_utilization": 1024.0,
            "ip_address": "192.168.1.2",
            "location": "datacenter-2",
        },
    ]
    mock_get_nodes.return_value = nodes
    transport = ASGITransport(app=app)
    # Set up the test client
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/node/")

    # Assertions
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 2  # Expecting two nodes in the response


@pytest.mark.asyncio
@patch("app.routes.node.get_nodes", new_callable=AsyncMock)
async def test_get_node_by_id(mock_get_nodes):
    # Sample node data
    nodes = [
        {
            "id": 1,
            "name": "test-node-1",
            "status": "active",
            "cpu_capacity": 4.0,
            "memory_capacity": 8192.0,
            "current_cpu_assignment": 1.0,
            "current_memory_assignment": 1024.0,
            "current_cpu_utilization": 0.5,
            "current_memory_utilization": 512.0,
            "ip_address": "192.168.1.1",
            "location": "datacenter-1",
        }
    ]
    mock_get_nodes.return_value = nodes
    transport = ASGITransport(app=app)
    # Test valid node ID
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/node/1")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == 1

    # Test invalid node ID
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/node/999")  # Non-existing node ID

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Node not found"


@pytest.mark.asyncio
@patch("app.crud.node.update_node", new_callable=AsyncMock)
async def test_update_node(mock_update_node):
    # Define request data and expected response data
    update_data = {
        "name": "updated-node",
        "status": "active",
        "cpu_capacity": 4.0,
        "memory_capacity": 8192.0,
        "current_cpu_assignment": 1.0,
        "current_memory_assignment": 1024.0,
        "current_cpu_utilization": 0.5,
        "current_memory_utilization": 512.0,
    }
    response_data = {
        "id": 1,
        "name": "updated-node",
        "status": "active",
        "cpu_capacity": 4.0,
        "memory_capacity": 8192.0,
        "current_cpu_assignment": 1.0,
        "current_memory_assignment": 1024.0,
        "current_cpu_utilization": 0.5,
        "current_memory_utilization": 512.0,
        "ip_address": "192.168.1.1",
        "location": "datacenter-1",
    }
    mock_update_node.return_value = response_data
    transport = ASGITransport(app=app)
    # Test the update functionality
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.put("/node/1", json=update_data)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == response_data


@pytest.mark.asyncio
@patch("app.crud.node.delete_node", new_callable=AsyncMock)
async def test_delete_node(mock_delete_node):
    # Simulate that node with ID 1 is deleted
    mock_delete_node.return_value = None
    transport = ASGITransport(app=app)
    # Set up the test client
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.delete("/node/1")

    # Assertions
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"detail": "Node deleted successfully"}
