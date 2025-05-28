"""Unit tests for the Node CRUD functions and routes."""

import json
from unittest.mock import MagicMock, AsyncMock, patch

import pytest
from fastapi import status
from httpx._transports.asgi import ASGITransport
from httpx import AsyncClient

from app.repositories.node import create_node, delete_node, get_nodes, update_node
from app.main import app
from app.schemas.node import NodeCreate, NodeResponse


# ===========================================================================
# ========================= Tests for node CRUD functions =========================
# ===========================================================================


@pytest.mark.asyncio
async def test_create_node():
    """
    Test the `create_node` function.

    Verifies that a node is added, committed, and refreshed using the DB session.
    """
    mock_db_session = AsyncMock()
    data = NodeCreate(
        id="c7e1f2a3-8b4d-4e2a-9c7b-1f5e3d2a8b6c",  # Example UUID
        name="node-1",
        status="active",
        cpu_capacity=4.0,
        memory_capacity=8192.0,
        ip_address="192.168.1.1",
        location="loc1",
    )

    node_instance = MagicMock()
    mock_db_session.add = MagicMock()
    mock_db_session.commit = AsyncMock()
    mock_db_session.refresh = AsyncMock()

    with patch("app.repositories.node.Node", return_value=node_instance):
        result = await create_node(mock_db_session, data)

    mock_db_session.add.assert_called_once_with(node_instance)
    mock_db_session.commit.assert_awaited_once()
    mock_db_session.refresh.assert_awaited_once_with(node_instance)
    assert result == node_instance


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "node_id, expected",
    [
        (None, ["node1", "node2"]),
        ("c7e1f2a3-8b4d-4e2a-9c7b-1f5e3d2a8b6c", ["filtered-node"]),
    ],
)
async def test_get_nodes(node_id, expected):
    """
    Test the `get_nodes` function.

    Args:
        node_id (UUID or None): If None, all nodes are fetched; otherwise, filtered by ID.
        expected (list): Expected return value from DB query.

    Asserts that returned results match expectations.
    """
    mock_db_session = AsyncMock()
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = expected
    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars
    mock_db_session.execute = AsyncMock(return_value=mock_result)

    result = await get_nodes(mock_db_session, node_id=node_id)
    assert result == expected


@pytest.mark.asyncio
async def test_update_node():
    """
    Test the `update_node` function.

    Ensures that the node is updated and the updated record is fetched correctly.
    """
    mock_db_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = {
        "id": "c7e1f2a3-8b4d-4e2a-9c7b-1f5e3d2a8b6c",
        "name": "updated-node",
    }

    mock_db_session.execute = AsyncMock(side_effect=[None, mock_result])
    mock_db_session.commit = AsyncMock()

    updates = {"name": "updated-node"}
    result = await update_node(
        mock_db_session, node_id="c7e1f2a3-8b4d-4e2a-9c7b-1f5e3d2a8b6c", updates=updates
    )

    assert result == {
        "id": "c7e1f2a3-8b4d-4e2a-9c7b-1f5e3d2a8b6c",
        "name": "updated-node",
    }
    assert mock_db_session.execute.await_count == 2
    mock_db_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_node():
    """
    Test the `delete_node` function.

    Verifies that the node is deleted and commit is called.
    """
    mock_db_session = AsyncMock()
    mock_db_session.execute = AsyncMock()
    mock_db_session.commit = AsyncMock()

    result = await delete_node(mock_db_session, node_id="c7e1f2a3-8b4d-4e2a-9c7b-1f5e3d2a8b6c")

    mock_db_session.execute.assert_awaited_once()
    mock_db_session.commit.assert_awaited_once()
    assert result == {"deleted_id": "c7e1f2a3-8b4d-4e2a-9c7b-1f5e3d2a8b6c"}


# =====================================================================================
# ========================= Below tests are for the node routes =========================
# =====================================================================================


@pytest.mark.asyncio
@patch("app.repositories.node.create_node", new_callable=AsyncMock)
async def test_create_node_api(mock_create_node):
    """
    Test POST /node/ endpoint.

    Mocks the `create_node` call and verifies response matches the schema.
    """

    request_data = NodeCreate(
        id="c7e1f2a3-8b4d-4e2a-9c7b-1f5e3d2a8b6c",  # Example UUID
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
        id="c7e1f2a3-8b4d-4e2a-9c7b-1f5e3d2a8b6c",
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
        response = await client.post(
            "/db_node/", json=json.loads(request_data.model_dump_json())
        )

    # Assertions
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == response_data.model_dump(mode="json")


@pytest.mark.asyncio
@patch("app.repositories.node.get_nodes", new_callable=AsyncMock)
async def test_get_nodes_api(mock_get_nodes):
    """
    Test GET /node/ endpoint.

    Ensures all mocked nodes are returned.
    """
    # Sample node data to be returned
    nodes = [
        {
            "id": "c7e1f2a3-8b4d-4e2a-9c7b-1f5e3d2a8b6c",
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
            "id": "b7e1f2a3-8b4d-4e2a-9c7b-1f5e3d2a8b6d",
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
        response = await client.get("/db_node/")

    # Assertions
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 2  # Expecting two nodes in the response


@pytest.mark.asyncio
@patch("app.repositories.node.update_node", new_callable=AsyncMock)
async def test_update_node_api(mock_update_node):
    """
    Test PUT /node/{node_id} endpoint.

    Checks that node is updated successfully.
    """
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
        "id": "c7e1f2a3-8b4d-4e2a-9c7b-1f5e3d2a8b6c",
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
        response = await client.put(
            "/db_node/c7e1f2a3-8b4d-4e2a-9c7b-1f5e3d2a8b6c", json=update_data
        )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == response_data


@pytest.mark.asyncio
@patch("app.repositories.node.delete_node", new_callable=AsyncMock)
async def test_delete_node_api(mock_delete_node):
    """
    Test DELETE /node/{node_id} endpoint.

    Ensures deletion confirmation message is returned.
    """
    # Simulate that node with ID 1 is deleted
    mock_delete_node.return_value = None
    transport = ASGITransport(app=app)
    # Set up the test client
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.delete("/db_node/c7e1f2a3-8b4d-4e2a-9c7b-1f5e3d2a8b6c")

    # Assertions
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"detail": "Node deleted successfully"}


@patch("app.repositories.node.get_node_by_id", new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_get_node_by_id_api(mock_get_node_by_id):
    """
    Test
    GET / node / {node_id} endpoint.

    Verifies correct response for existing and non-existing node IDs.
    """
    mock_get_node_by_id.return_value = {
        "id": "c7e1f2a3-8b4d-4e2a-9c7b-1f5e3d2a8b6c",
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
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/db_node/c7e1f2a3-8b4d-4e2a-9c7b-1f5e3d2a8b6c")

    assert response.status_code == 200
    assert response.json()["id"] == "c7e1f2a3-8b4d-4e2a-9c7b-1f5e3d2a8b6c"
