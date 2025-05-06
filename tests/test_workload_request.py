import pytest
from httpx import AsyncClient
from httpx._transports.asgi import ASGITransport
from fastapi import status
from unittest.mock import AsyncMock, patch, MagicMock
from app.main import app
from app.crud.workload_request import (
    create_workload_request,
    get_workload_requests,
    update_workload_request,
    delete_workload_request,
)
from app.models import WorkloadRequest
from app.schemas import WorkloadRequestCreate





@pytest.mark.asyncio
@patch("app.crud.workload_request.WorkloadRequest")
async def test_create_workload_request(mock_work):
    """
    Test the creation of a new workload request using mocked CRUD logic.
    Asserts that the POST request returns a 200 status and correct JSON response.
    """
    db_call = AsyncMock()
    mock_wr_obj = MagicMock()
    mock_work.return_value = mock_wr_obj

    data = WorkloadRequestCreate(
        name="demo",
        namespace="default",
        api_version="v1",
        kind="Deployment",
        current_scale=1,
    )
    result = await create_workload_request(db_call, data)
    db_call.add.assert_called_once_with(mock_wr_obj)
    db_call.commit.assert_awaited_once()
    db_call.refresh.assert_awaited_once_with(mock_wr_obj)
    assert result == mock_wr_obj


async def test_get_workload_requests_no_filters():
    db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = ["obj1", "obj2"]
    db.execute.return_value = mock_result

    result = await get_workload_requests(db)

    db.execute.assert_awaited_once()
    assert result == ["obj1", "obj2"]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "kargs, expected_filters",
    [
        ({"workload_request_id": 1}, [WorkloadRequest.id == 1]),
        ({"name": "test"}, [WorkloadRequest.name == "test"]),
        ({"namespace": "default"}, [WorkloadRequest.namespace == "default"]),
        ({"api_version": "v1"}, [WorkloadRequest.api_version == "v1"]),
        ({"kind": "Deployment"}, [WorkloadRequest.kind == "Deployment"]),
        ({"current_scale": 3}, [WorkloadRequest.current_scale == 3]),
    ],
)
async def test_get_workload_requests_with_individual_filters(kargs, expected_filters):
    db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = ["filtered"]
    db.execute.return_value = mock_result

    result = await get_workload_requests(db, **kargs)

    db.execute.assert_awaited_once()
    assert result == ["filtered"]


@pytest.mark.asyncio
async def test_get_workload_requests_with_multiple_filters():
    db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = ["combo"]
    db.execute.return_value = mock_result

    result = await get_workload_requests(
        db,
        workload_request_id=1,
        name="demo",
        namespace="default",
        api_version="v1",
        kind="Deployment",
        current_scale=2,
    )

    db.execute.assert_awaited_once()
    assert result == ["combo"]


async def test_update_workload_request():
    """
    Test updating an existing workload request.
    Checks that the PUT request returns updated data from the mock.
    """
    db = AsyncMock()
    mock_result = MagicMock()
    mock_workload_request = MagicMock()
    db.execute.return_value = mock_result
    mock_result.scalar_one_or_none.return_value = mock_workload_request

    updates = {"name": "Deployment"}
    result = await update_workload_request(db, 1, updates)
    db.execute.assert_awaited_once()
    assert mock_workload_request.name == "Deployment"
    db.add.assert_called_once_with(mock_workload_request)
    db.commit.assert_awaited_once()
    db.refresh.assert_awaited_once_with(mock_workload_request)
    assert result == mock_workload_request


async def test_delete_workload_request():
    """
    Test deleting a workload request.
    Ensures the DELETE request returns a confirmation of deletion.
    """
    # Arrange

    db = AsyncMock()
    mock_result = MagicMock()
    mock_workload_request = MagicMock()
    db.execute.return_value = mock_result
    mock_result.scalar_one_or_none.return_value = mock_workload_request

    # Act

    result = await delete_workload_request(db, 1)

    # Assertion

    db.execute.assert_awaited_once()
    db.delete.assert_awaited_once_with(mock_workload_request)
    db.commit.assert_awaited_once()
    assert result == {"message": "WorkloadRequest with ID 1 has been deleted"}


@pytest.mark.asyncio
async def test_update_workload_request_not_found():
    db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    db.execute.return_value = mock_result

    result = await update_workload_request(db, 999, {"name": "new-name"})

    db.execute.assert_awaited_once()
    assert result is None
    db.add.assert_not_called()
    db.commit.assert_not_called()
    db.refresh.assert_not_called()


@pytest.mark.asyncio
async def test_update_workload_request_ignores_invalid_fields():
    db = AsyncMock()
    mock_result = MagicMock()
    mock_workload_request = MagicMock()

    mock_result.scalar_one_or_none.return_value = mock_workload_request
    db.execute.return_value = mock_result

    updates = {"invalid_field": "value"}  # should be ignored

    result = await update_workload_request(db, 1, updates)

    db.add.assert_called_once_with(mock_workload_request)
    db.commit.assert_awaited_once()
    db.refresh.assert_awaited_once_with(mock_workload_request)
    assert result == mock_workload_request


async def test_delete_workload_request_not_found():
    """
    Test deleting a workload request.
    Ensures the DELETE request returns a confirmation of deletion.
    """
    # Arrange

    db = AsyncMock()
    mock_result = MagicMock()
    db.execute.return_value = mock_result
    mock_result.scalar_one_or_none.return_value = None

    # Act

    result = await delete_workload_request(db, None)

    # Assertion

    db.execute.assert_awaited_once()
    assert result == {"error": "WorkloadRequest not found"}


# =====================================================================================
# ========================= Below tests are for the workload_request routes =========================
# =====================================================================================

@pytest.mark.asyncio
@patch("app.crud.create_workload_request", new_callable=AsyncMock)
async def test_create_workload_request_route(mock_create):
    """
    Test the creation of a new workload request using mocked CRUD logic.
    Asserts that the POST request returns a 200 status and correct JSON response.
    """

    request_data = {
        "name": "test-workload",
        "namespace": "default",
        "api_version": "v1",
        "kind": "Deployment",
        "current_scale": 3
    }

    response_data = {
        "id": 1,
        "name": "test-workload",
        "namespace": "default",
        "api_version": "v1",
        "kind": "Deployment",
        "current_scale": 3,
        "created_at": "2023-01-01T12:00:00Z",
        "updated_at": "2023-01-01T12:00:00Z"
    }

    mock_create.return_value = response_data

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/workload_request/", json=request_data)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == response_data


@pytest.mark.asyncio
@patch("app.crud.update_workload_request", new_callable=AsyncMock)
async def test_update_workload_request_route(mock_update):
    """
    Test updating a workload request using mocked CRUD logic.
    Asserts that the PUT request returns a 200 status and correct JSON response.
    """

    request_data = {
        "current_scale": 5
    }

    response_data = {
        "id": 1,
        "name": "test-workload",
        "namespace": "default",
        "api_version": "v1",
        "kind": "Deployment",
        "current_scale": 5,
        "created_at": "2023-01-01T12:00:00Z",
        "updated_at": "2023-01-01T12:30:00Z"
    }

    mock_update.return_value = response_data

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.put("/workload_request/1", json=request_data)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == response_data


@pytest.mark.asyncio
@patch("app.crud.delete_workload_request", new_callable=AsyncMock)
async def test_delete_workload_request_route(mock_delete):
    """
    Test deleting a workload request using mocked CRUD logic.
    Asserts that the DELETE request returns a 200 status and correct JSON response.
    """

    response_data = {"message": "Workload request with ID 1 has been deleted"}

    mock_delete.return_value = response_data

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.delete("/workload_request/1")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == response_data


@pytest.mark.asyncio
@patch("app.crud.get_workload_requests", new_callable=AsyncMock)
async def test_read_workload_requests_route(mock_get):
    """
    Test retrieving workload requests using mocked CRUD logic.
    Asserts that the GET request returns a 200 status and correct JSON response.
    """

    response_data = [
        {
            "id": 1,
            "name": "test-workload",
            "namespace": "default",
            "api_version": "v1",
            "kind": "Deployment",
            "current_scale": 3,
            "created_at": "2023-01-01T12:00:00Z",
            "updated_at": "2023-01-01T12:00:00Z"
        }
    ]

    mock_get.return_value = response_data

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/workload_request/")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == response_data


@pytest.mark.asyncio
@patch("app.crud.get_workload_requests", new_callable=AsyncMock)
async def test_read_workload_request_by_id_route(mock_get):
    """
    Test retrieving a specific workload request by ID using mocked CRUD logic.
    Asserts that the GET request returns a 200 status and correct JSON response.
    """

    response_data = {
        "id": 1,
        "name": "test-workload",
        "namespace": "default",
        "api_version": "v1",
        "kind": "Deployment",
        "current_scale": 3,
        "created_at": "2023-01-01T12:00:00Z",
        "updated_at": "2023-01-01T12:00:00Z"
    }

    mock_get.return_value = response_data

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/workload_request/1")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == response_data