import pytest
from httpx import AsyncClient
from httpx._transports.asgi import ASGITransport
from fastapi import status
from unittest.mock import AsyncMock, patch
from app.main import app


@pytest.mark.asyncio
@patch("app.crud.create_workload_request", new_callable=AsyncMock)
async def test_create_workload_request(mock_create):
    """
    Test the creation of a new workload request using mocked CRUD logic.
    Asserts that the POST request returns a 200 status and correct JSON response.
    """
    mock_create.return_value = {"id": 1, "name": "demo"}

    data = {
        "name": "demo",
        "namespace": "default",
        "api_version": "v1",
        "kind": "Deployment",
        "current_scale": 1,
    }

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/workload_request/", json=data)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"id": 1, "name": "demo"}


@pytest.mark.asyncio
@patch("app.routes.workload_request.crud.get_workload_requests", new_callable=AsyncMock)
async def test_read_workload_requests(mock_get):
    """
    Test fetching all workload requests.
    Verifies that the GET request returns expected mocked data.
    """
    mock_get.return_value = [{"id": 1, "name": "demo"}]
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/workload_request/")

    assert response.status_code == status.HTTP_200_OK

    assert response.json() == [{"id": 1, "name": "demo"}]


@pytest.mark.asyncio
@patch(
    "app.routes.workload_request.crud.update_workload_request", new_callable=AsyncMock
)
async def test_update_workload_request(mock_update):
    """
    Test updating an existing workload request.
    Checks that the PUT request returns updated data from the mock.
    """
    mock_update.return_value = {"id": 1, "name": "updated"}

    update_data = {"name": "updated"}
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.put("/workload_request/1", json=update_data)

    assert response.status_code == status.HTTP_200_OK

    assert response.json()["name"] == "updated"


@pytest.mark.asyncio
@patch(
    "app.routes.workload_request.crud.delete_workload_request", new_callable=AsyncMock
)
async def test_delete_workload_request(mock_delete):
    """
    Test deleting a workload request.
    Ensures the DELETE request returns a confirmation of deletion.
    """
    mock_delete.return_value = {"status": "deleted"}
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.delete("/workload_request/1")

    assert response.status_code == status.HTTP_200_OK

    assert response.json() == {"status": "deleted"}


@pytest.mark.asyncio
@patch("app.routes.workload_request.crud.get_workload_requests", new_callable=AsyncMock)
async def test_read_workload_request_by_id(mock_get):
    """
    Test fetching a specific workload request by ID.
    Verifies that the response includes the correct item.
    """
    mock_get.return_value = {"id": 1, "name": "demo"}
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/workload_request/1")

    assert response.status_code == status.HTTP_200_OK

    assert response.json()["id"] == 1
