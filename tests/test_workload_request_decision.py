"""
Tests for workload_request_decision CRUD functions and routes.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import status
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.crud import workload_request_decision as wrd
from app.models import WorkloadRequestDecision
from app.schemas import WorkloadRequestDecisionCreate


# ===========================================================================
# ======= Tests for workload_request_decision CRUD functions ================
# ===========================================================================
@pytest.mark.asyncio
async def test_create_workload_request_decision():
    """
    Test the creation of a new workload request decision.
    """
    db = AsyncMock()
    decision_data = WorkloadRequestDecisionCreate(
        workload_request_id=1,
        node_name="node-1",
        queue_name="queue-1",
        status="pending",
    )
    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    result = await wrd.create_workload_request_decision(db, decision_data)

    db.add.assert_called_once()
    db.commit.assert_called_once()
    db.refresh.assert_called_once()
    assert isinstance(result, WorkloadRequestDecision)


@pytest.mark.asyncio
async def test_update_workload_request_decision():
    """
    Test the update_workload_request_decision function
    """
    db = AsyncMock()
    mock_decision = MagicMock(spec=WorkloadRequestDecision, status="pending")
    # Directly return the mock_decision
    db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=mock_decision))
    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    updates = {"status": "approved"}
    result = await wrd.update_workload_request_decision(
        db, workload_request_id=1, updates=updates
    )

    db.execute.assert_called_once()
    db.commit.assert_called_once()
    db.refresh.assert_called_once()
    assert result is not None
    assert result.status == "approved"


@pytest.mark.asyncio
async def test_delete_workload_request_decision():
    """
    Test the delete_workload_request_decision function
    """
    db = AsyncMock()
    mock_decision = WorkloadRequestDecision()
    db.execute = AsyncMock(
        return_value=MagicMock(
            scalars=MagicMock(all=MagicMock(return_value=[mock_decision]))
        )
    )
    db.delete = AsyncMock()
    db.commit = AsyncMock()

    result = await wrd.delete_workload_request_decision(db, workload_request_id=1)

    db.execute.assert_called_once()
    db.delete.assert_called()
    db.commit.assert_called_once()
    assert result["message"] == "Decision with ID 1 has been deleted"


@pytest.mark.asyncio
async def test_get_workload_request_decision():
    """
    Test the get_workload_request_decision function
    """
    # Mock data
    mock_decision = MagicMock(spec=WorkloadRequestDecision)
    mock_decision.workload_request_id = 1
    mock_decision.node_name = "node-1"
    mock_decision.queue_name = "queue-1"
    mock_decision.status = "pending"

    # Mock the return value of result.scalars().all()
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = [mock_decision]

    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars

    db = AsyncMock()
    db.execute.return_value = mock_result

    # Call the function
    result = await wrd.get_workload_request_decision(
        db,
        workload_request_id=1,
        node_name="node-1",
        queue_name="queue-1",
        status="pending",
    )

    # Assertions
    db.execute.assert_called_once()
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0].workload_request_id == 1
    assert result[0].status == "pending"


# =====================================================================================
# ====== Below tests are for the workload_request_decision routes =====================
# =====================================================================================


@pytest.mark.asyncio
@patch(
    "app.crud.workload_request_decision.create_workload_request_decision",
    new_callable=AsyncMock,
)
async def test_create_workload_request_decision_route(mock_create):
    """
    Test the creation of a new workload request decision using mocked CRUD logic.
    Asserts that the POST request returns a 200 status and correct JSON response.
    """

    request_data = {
        "workload_request_id": 1,
        "node_name": "node-1",
        "queue_name": "queue-1",
        "status": "pending",
    }
    response_data = {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "workload_request_id": 1,
        "node_name": "node-1",
        "queue_name": "queue-1",
        "status": "pending",
        "created_at": "2023-02-01T12:00:00Z",
        "updated_at": "2023-02-01T12:00:00Z",
    }

    mock_create.return_value = response_data

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/workload_request_decision/", json=request_data)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == response_data


@pytest.mark.asyncio
@patch(
    "app.crud.workload_request_decision.update_workload_request_decision",
    new_callable=AsyncMock,
)
async def test_update_workload_request_decision_route(mock_update):
    """
    Test updating a workload request decision using mocked CRUD logic.
    Asserts that the PUT request returns a 200 status and correct JSON response.
    """
    request_data = {"status": "approved"}
    response_data = {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "workload_request_id": 1,
        "node_name": "node-1",
        "queue_name": "queue-1",
        "status": "approved",
        "created_at": "2023-02-01T12:00:00Z",
        "updated_at": "2023-02-01T12:30:00Z",
    }

    mock_update.return_value = response_data

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.put("/workload_request_decision/1", json=request_data)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == response_data


@pytest.mark.asyncio
@patch(
    "app.crud.workload_request_decision.delete_workload_request_decision",
    new_callable=AsyncMock,
)
async def test_delete_workload_request_decision_route(mock_delete):
    """
    Test deleting a workload request decision using mocked CRUD logic.
    Asserts that the DELETE request returns a 200 status and correct JSON response.
    """
    response_data = {"message": "Decision with ID 1 has been deleted"}

    mock_delete.return_value = response_data

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.delete("/workload_request_decision/1")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == response_data


@pytest.mark.asyncio
@patch(
    "app.crud.workload_request_decision.get_workload_request_decision",
    new_callable=AsyncMock,
)
async def test_get_workload_request_decision_route(mock_get):
    """
    Test retrieving workload request decisions using mocked CRUD logic.
    Asserts that the GET request returns a 200 status and correct JSON response.
    """
    response_data = [
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "workload_request_id": 1,
            "node_name": "node-1",
            "queue_name": "queue-1",
            "status": "pending",
            "created_at": "2023-02-01T12:00:00Z",
            "updated_at": "2023-02-01T12:00:00Z",
        }
    ]

    mock_get.return_value = response_data

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/workload_request_decision/")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == response_data


@pytest.mark.asyncio
@patch(
    "app.crud.workload_request_decision.get_workload_request_decision",
    new_callable=AsyncMock,
)
async def test_get_workload_request_decision_by_id_route(mock_get):
    """
    Test retrieving a specific workload request decision by ID using mocked CRUD logic.
    Asserts that the GET request returns a 200 status and correct JSON response.
    """
    response_data = {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "workload_request_id": 1,
        "node_name": "node-1",
        "queue_name": "queue-1",
        "status": "pending",
        "created_at": "2023-02-01T12:00:00Z",
        "updated_at": "2023-02-01T12:00:00Z",
    }

    mock_get.return_value = response_data

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/workload_request_decision/1")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == response_data
