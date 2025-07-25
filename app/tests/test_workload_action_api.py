"""
Test cases for the workload action API endpoints.
This module tests the creation, retrieval, listing, updating, 
and deletion of workload actions through the API.
"""

from unittest.mock import AsyncMock, patch
from uuid import uuid4
import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.tests.utils.mock_objects import (
    TEST_UUID,
    mock_workload_action_create_obj,
    mock_workload_action_obj,
    mock_workload_action_update_obj,
    to_jsonable,
)


@pytest.mark.asyncio
@patch("app.api.workload_action_api.create_workload_action", new_callable=AsyncMock)
async def test_create_workload_action_route(mock_create):
    """Test creating a workload action."""
    data = mock_workload_action_create_obj(action_id=TEST_UUID).model_dump()
    data = to_jsonable(data)
    mock_create.return_value = mock_workload_action_obj(
        action_id=TEST_UUID
    ).model_dump()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/workload_action/", json=data)
    assert response.status_code == 200
    assert response.json()["id"] == TEST_UUID
    mock_create.assert_awaited_once()


@pytest.mark.asyncio
@patch("app.api.workload_action_api.get_workload_action_by_id", new_callable=AsyncMock)
async def test_get_workload_action_route(mock_get):
    """Test getting a workload action by ID."""
    mock_get.return_value = mock_workload_action_obj(
        action_id=TEST_UUID, action_type="Bind"
    ).model_dump()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get(f"/workload_action/{TEST_UUID}")
    assert response.status_code == 200
    assert response.json()["id"] == TEST_UUID
    mock_get.assert_awaited_once()


@pytest.mark.asyncio
@patch("app.api.workload_action_api.list_workload_actions", new_callable=AsyncMock)
async def test_get_all_workload_actions_route(mock_list):
    """Test listing all workload actions."""
    random_uuid = str(uuid4())
    mock_list.return_value = [
        mock_workload_action_obj(action_id=TEST_UUID, action_type="Bind").model_dump(),
        mock_workload_action_obj(
            action_id=random_uuid, action_type="Create"
        ).model_dump(),
    ]
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/workload_action/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert response.json()[0]["id"] == TEST_UUID
    assert response.json()[1]["id"] == random_uuid
    mock_list.assert_awaited_once()


@pytest.mark.asyncio
@patch("app.api.workload_action_api.update_workload_action", new_callable=AsyncMock)
async def test_update_workload_action_route(mock_update):
    """Test updating a workload action."""
    update_data = mock_workload_action_update_obj(
        action_status="successful"
    ).model_dump()
    update_data = to_jsonable(update_data)
    mock_update.return_value = mock_workload_action_obj(
        action_id=TEST_UUID, action_status="successful"
    )
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.put(f"/workload_action/{TEST_UUID}", json=update_data)
    assert response.status_code == 200
    assert response.json()["id"] == TEST_UUID
    assert response.json()["action_status"] == "successful"
    mock_update.assert_awaited_once()


@pytest.mark.asyncio
@patch("app.api.workload_action_api.delete_workload_action", new_callable=AsyncMock)
async def test_delete_workload_action_route(mock_delete):
    """Test deleting a workload action."""
    mock_delete.return_value = True
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.delete(f"/workload_action/{TEST_UUID}")
    assert response.status_code == 200
    assert response.json() is True
    mock_delete.assert_awaited_once()
