import pytest
from unittest.mock import MagicMock
from app.crud.node import create_node, get_nodes, update_node, delete_node
from app.schemas import NodeCreate
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from app.main import app

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


@pytest.fixture
def client():
    return TestClient(app)


@pytest.mark.asyncio
@patch("app.crud.node.create_node")
async def test_create_node(mock_create_node, client):
    # Arrange
    new_node_data = {
        "name": "node-1",
        "status": "active",
        "cpu_capacity": 4.0,
        "memory_capacity": 8192.0,
        "ip_address": "192.168.1.1",
        "location": "loc1",
    }

    # Mocking the database call to return the full NodeResponse schema
    mock_create_node.return_value = {
        "id": 1,
        "name": "node-1",
        "status": "active",
        "cpu_capacity": 4.0,
        "memory_capacity": 8192.0,
        "ip_address": "192.168.1.1",
        "location": "loc1",
        "current_cpu_assignment": None,
        "current_cpu_utilization": None,
        "current_memory_assignment": None,
        "current_memory_utilization": None,
    }

    # Act
    response = client.post("/node/", json=new_node_data)

    # Assert
    assert response.status_code == 200
    assert response.json() == mock_create_node.return_value


@pytest.mark.asyncio
@patch("app.crud.node.get_nodes")
async def test_get_nodes(mock_get_nodes, client):
    # Arrange
    mock_get_nodes.return_value = [
        {
            "id": 1,
            "name": "node-1",
            "status": "active",
            "cpu_capacity": 4.0,
            "memory_capacity": 8192.0,
            "ip_address": "192.168.1.1",
            "location": "loc1",
        },
        {
            "id": 2,
            "name": "node-2",
            "status": "inactive",
            "cpu_capacity": 8.0,
            "memory_capacity": 16384.0,
            "ip_address": "192.168.1.2",
            "location": "loc2",
        },
    ]

    # Act
    response = client.get("/node/")

    # Assert
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["name"] == "node-1"
    assert response.json()[1]["name"] == "node-2"


@pytest.mark.asyncio
@patch(
    "app.crud.node.get_nodes"
)  # Mocking the 'get_nodes' function in the 'crud/node.py'
async def test_get_node_by_id(mock_get_nodes, client):
    # Arrange: Mock data returned by the 'get_nodes' function (Node exists)
    mock_get_nodes.return_value = [
        {
            "id": 1,
            "name": "node-1",
            "status": "active",
            "cpu_capacity": 4.0,
            "memory_capacity": 8192.0,
            "ip_address": "192.168.1.1",
            "location": "loc1",
            "current_cpu_assignment": None,
            "current_cpu_utilization": None,
            "current_memory_assignment": None,
            "current_memory_utilization": None,
        }
    ]

    # Act: Send the GET request for the existing node with id = 1
    response = client.get("/node/1")

    # Assert: Check the response status and data
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["id"] == 1
    assert response_data["name"] == "node-1"
    assert response_data["status"] == "active"

    # Act for non-existent node (node_id = 999) - Mock to return an empty list for non-existent nodes
    mock_get_nodes.return_value = []  # Mock that no nodes are returned for id 999
    response = client.get("/node/999")

    # Assert: Check the response for a non-existent node
    assert (
        response.status_code == 404
    )  # Or 200 if you're using a 200 status code with an error message
    assert response.json() == {"detail": "Node not found"}


@pytest.mark.asyncio
@patch("app.crud.node.update_node")
async def test_update_node(mock_update_node, client):
    # Arrange
    updated_node_data = {
        "name": "node-1-updated",
        "status": "active",
        "cpu_capacity": 6.0,
        "memory_capacity": 16384.0,
        "ip_address": "192.168.1.10",
        "location": "loc1",
    }

    mock_update_node.return_value = {
        "id": 1,
        "name": "node-1-updated",
        "status": "active",
        "cpu_capacity": 6.0,
        "memory_capacity": 16384.0,
        "ip_address": "192.168.1.10",
        "location": "loc1",
    }

    # Act
    response = client.put("/node/1", json=updated_node_data)

    # Assert
    assert response.status_code == 200
    assert response.json()["name"] == "node-1-updated"
    assert response.json()["cpu_capacity"] == 6.0


@pytest.mark.asyncio
@patch("app.crud.node.delete_node")
async def test_delete_node(mock_delete_node, client):
    # Arrange
    mock_delete_node.return_value = {"message": "Node deleted successfully"}

    # Act
    response = client.delete("/node/1")

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": "Node deleted successfully"}
