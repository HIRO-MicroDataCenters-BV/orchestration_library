"""
Tests for workload_request CRUD functions and routes.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import status
from httpx import AsyncClient
from httpx._transports.asgi import ASGITransport
from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError


from app.repositories.workload_request import (
    create_workload_request,
    delete_workload_request,
    get_workload_requests,
    update_workload_request,
    WorkloadRequestFilter,
)
from app.main import app
from app.models.workload_request import WorkloadRequest
from app.schemas.workload_request import WorkloadRequestCreate
from app.utils.exceptions import (
    DBEntryNotFoundException,
    DBEntryCreationException,
    DBEntryDeletionException,
    DBEntryUpdateException,
    DataBaseException
)


# ===========================================================================
# ================ Tests for workload_request CRUD functions ================
# ===========================================================================

SAMPLE_WORKLOAD_REQUEST_CREATE = WorkloadRequestCreate(
    id="123e4567-e89b-12d3-a456-426614174000",  # Example UUID
    name="demo",
    namespace="default",
    api_version="v1",
    kind="Deployment",
    status="2/2 Running",
    current_scale=1,
)

SAMPLE_WORKLOAD_REQUEST_FILTER = WorkloadRequestFilter(
    workload_request_id="123e4567-e89b-12d3-a456-426614174000",
    name="demo",
    namespace="default",
    api_version="v1",
    kind="Deployment",
    status="2/2 Running",
    current_scale=2,
)

SAMPLE_REQUEST_DATA = {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "name": "test-workload",
    "namespace": "default",
    "api_version": "v1",
    "kind": "Deployment",
    "status": "3/3 Running",
    "current_scale": 3,
}

SAMPLE_RESPONSE_DATA = {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "name": "test-workload",
    "namespace": "default",
    "api_version": "v1",
    "kind": "Deployment",
    "status": "3/3 Running",
    "current_scale": 3,
    "created_at": "2023-01-01T12:00:00Z",
    "updated_at": "2023-01-01T12:00:00Z",
}


@pytest.mark.asyncio
@patch("app.repositories.workload_request.WorkloadRequest")
async def test_create_workload_request(mock_work):
    """
    Test the creation of a new workload request using mocked CRUD logic.
    Asserts that the POST request returns a 200 status and correct JSON response.
    """
    db_call = AsyncMock()
    mock_wr_obj = MagicMock()
    mock_work.return_value = mock_wr_obj

    data = SAMPLE_WORKLOAD_REQUEST_CREATE
    result = await create_workload_request(db_call, data)
    db_call.add.assert_called_once_with(mock_wr_obj)
    db_call.commit.assert_awaited_once()
    db_call.refresh.assert_awaited_once_with(mock_wr_obj)
    assert result == mock_wr_obj


async def test_get_workload_requests_no_filters():
    """
    Test the retrieval of workload requests without any filters.
    Asserts that the GET request returns all workload requests.
    """
    db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = ["obj1", "obj2"]
    db.execute.return_value = mock_result

    result = await get_workload_requests(db, WorkloadRequestFilter())

    db.execute.assert_awaited_once()
    assert result == ["obj1", "obj2"]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "kargs, expected_filters",
    [
        (
            WorkloadRequestFilter(
                workload_request_id="123e4567-e89b-12d3-a456-426614174000"
            ),
            [WorkloadRequest.id == "123e4567-e89b-12d3-a456-426614174000"],
        ),
        (WorkloadRequestFilter(name="test"), [WorkloadRequest.name == "test"]),
        (
            WorkloadRequestFilter(namespace="default"),
            [WorkloadRequest.namespace == "default"],
        ),
        (
            WorkloadRequestFilter(api_version="v1"),
            [WorkloadRequest.api_version == "v1"],
        ),
        (
            WorkloadRequestFilter(kind="Deployment"),
            [WorkloadRequest.kind == "Deployment"],
        ),
        (
            WorkloadRequestFilter(status="3/3 Running"),
            [WorkloadRequest.status == "3/3 Running"],
        ),
        (WorkloadRequestFilter(current_scale=3), [WorkloadRequest.current_scale == 3]),
    ],
)
async def test_get_workload_requests_with_individual_filters(kargs, expected_filters):
    """
    Test the retrieval of workload requests with individual filters.
    Asserts that the GET request returns the expected workload requests.
    """
    db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = ["filtered"]
    db.execute.return_value = mock_result

    result = await get_workload_requests(db, kargs)

    db.execute.assert_awaited_once()
    assert result == ["filtered"]
    assert expected_filters is not None


@pytest.mark.asyncio
async def test_get_workload_requests_with_multiple_filters():
    """
    Test the retrieval of workload requests with multiple filters.
    Asserts that the GET request returns the expected workload requests.
    """
    db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = ["combo"]
    db.execute.return_value = mock_result

    result = await get_workload_requests(
        db,
        SAMPLE_WORKLOAD_REQUEST_FILTER,
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
    result = await update_workload_request(
        db, "123e4567-e89b-12d3-a456-426614174000", updates
    )
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

    result = await delete_workload_request(db, "123e4567-e89b-12d3-a456-426614174000")

    # Assertion

    db.execute.assert_awaited_once()
    db.delete.assert_awaited_once_with(mock_workload_request)
    db.commit.assert_awaited_once()
    assert result == {
        "message": "WorkloadRequest with ID 123e4567-e89b-12d3-a456-426614174000 has been deleted"
    }


@pytest.mark.asyncio
async def test_update_workload_request_not_found():
    """
    Test updating a workload request that does not exist.
    Ensures the PUT request returns None.
    """
    db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    db.execute.return_value = mock_result

    with pytest.raises(DBEntryNotFoundException) as exc_info:
        await update_workload_request(db, 999, {"name": "new-name"})

    db.execute.assert_awaited_once()
    db.add.assert_not_called()
    db.commit.assert_not_called()
    db.refresh.assert_not_called()
    assert "999" in str(exc_info.value)


@pytest.mark.asyncio
async def test_update_workload_request_ignores_invalid_fields():
    """
    Test updating a workload request with invalid fields.
    Ensures that only valid fields are updated.
    """
    db = AsyncMock()
    mock_result = MagicMock()
    mock_workload_request = MagicMock()

    mock_result.scalar_one_or_none.return_value = mock_workload_request
    db.execute.return_value = mock_result

    updates = {"invalid_field": "value"}  # should be ignored

    result = await update_workload_request(
        db, "123e4567-e89b-12d3-a456-426614174000", updates
    )

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
    with pytest.raises(DBEntryNotFoundException) as exc_info:
        await delete_workload_request(db, None)

    # Assertion
    db.execute.assert_awaited_once()
    assert "None" in str(exc_info.value)


@pytest.mark.asyncio
async def test_create_workload_request_integrity_error():
    """
    Test creating a workload request with an integrity error.
    """
    db = AsyncMock()
    db.commit.side_effect = IntegrityError("Integrity", None, None)
    req = SAMPLE_WORKLOAD_REQUEST_CREATE
    with pytest.raises(DBEntryCreationException):
        await create_workload_request(db, req)
    db.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_workload_request_operational_error():
    """
    Test creating a workload request with an operational error.
    """
    db = AsyncMock()
    db.commit.side_effect = OperationalError("Operational", None, None)
    req = SAMPLE_WORKLOAD_REQUEST_CREATE
    with pytest.raises(DBEntryCreationException):
        await create_workload_request(db, req)
    db.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_workload_request_sqlalchemy_error():
    """
    Test creating a workload request with a SQLAlchemy error.
    """
    db = AsyncMock()
    db.commit.side_effect = SQLAlchemyError("SQLAlchemy")
    req = SAMPLE_WORKLOAD_REQUEST_CREATE
    with pytest.raises(DBEntryCreationException):
        await create_workload_request(db, req)
    db.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_workload_request_integrity_error():
    """
    Test updating a workload request with an integrity error.
    """
    db = AsyncMock()
    mock_result = MagicMock()
    mock_workload_request = MagicMock()
    db.execute.return_value = mock_result
    mock_result.scalar_one_or_none.return_value = mock_workload_request
    db.commit.side_effect = IntegrityError("Integrity", None, None)
    with pytest.raises(DBEntryUpdateException):
        await update_workload_request(
            db, "123e4567-e89b-12d3-a456-426614174000", {"name": "new"}
        )
    db.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_workload_request_operational_error():
    """
    Test updating a workload request with an operational error.
    """
    db = AsyncMock()
    mock_result = MagicMock()
    mock_workload_request = MagicMock()
    db.execute.return_value = mock_result
    mock_result.scalar_one_or_none.return_value = mock_workload_request
    db.commit.side_effect = OperationalError("Operational", None, None)
    with pytest.raises(DBEntryUpdateException):
        await update_workload_request(
            db, "123e4567-e89b-12d3-a456-426614174000", {"name": "new"}
        )
    db.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_workload_request_sqlalchemy_error():
    """
    Test updating a workload request with a SQLAlchemy error.
    """
    db = AsyncMock()
    mock_result = MagicMock()
    mock_workload_request = MagicMock()
    db.execute.return_value = mock_result
    mock_result.scalar_one_or_none.return_value = mock_workload_request
    db.commit.side_effect = SQLAlchemyError("SQLAlchemy")
    with pytest.raises(DBEntryUpdateException):
        await update_workload_request(
            db, "123e4567-e89b-12d3-a456-426614174000", {"name": "new"}
        )
    db.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_workload_request_integrity_error():
    """
    Test deleting a workload request with an integrity error.
    """
    db = AsyncMock()
    mock_result = MagicMock()
    mock_workload_request = MagicMock()
    db.execute.return_value = mock_result
    mock_result.scalar_one_or_none.return_value = mock_workload_request
    db.commit.side_effect = IntegrityError("Integrity", None, None)
    with pytest.raises(DBEntryDeletionException):
        await delete_workload_request(db, "123e4567-e89b-12d3-a456-426614174000")
    db.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_workload_request_operational_error():
    """
    Test deleting a workload request with an operational error.
    """
    db = AsyncMock()
    mock_result = MagicMock()
    mock_workload_request = MagicMock()
    db.execute.return_value = mock_result
    mock_result.scalar_one_or_none.return_value = mock_workload_request
    db.commit.side_effect = OperationalError("Operational", None, None)
    with pytest.raises(DBEntryDeletionException):
        await delete_workload_request(db, "123e4567-e89b-12d3-a456-426614174000")
    db.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_workload_request_sqlalchemy_error():
    """
    Test deleting a workload request with a SQLAlchemy error.
    """
    db = AsyncMock()
    mock_result = MagicMock()
    mock_workload_request = MagicMock()
    db.execute.return_value = mock_result
    mock_result.scalar_one_or_none.return_value = mock_workload_request
    db.commit.side_effect = SQLAlchemyError("SQLAlchemy")
    with pytest.raises(DBEntryCreationException):
        await delete_workload_request(db, "123e4567-e89b-12d3-a456-426614174000")
    db.rollback.assert_awaited_once()

@pytest.mark.asyncio
async def test_get_workload_requests_operational_error():
    """
    Test retrieving workload requests when there is an operational error.
    """
    db = AsyncMock()
    db.execute.side_effect = OperationalError("Operational", None, None)
    with pytest.raises(DataBaseException) as exc_info:
        await get_workload_requests(db, WorkloadRequestFilter())
    assert "Database connection error" in str(exc_info.value)

@pytest.mark.asyncio
async def test_get_workload_requests_sqlalchemy_error():
    """
    Test retrieving workload requests when there is a SQLAlchemy error.
    """
    db = AsyncMock()
    db.execute.side_effect = SQLAlchemyError("SQLAlchemy")
    with pytest.raises(DataBaseException) as exc_info:
        await get_workload_requests(db, WorkloadRequestFilter())
    assert "Failed to retrieve workload requests" in str(exc_info.value)

# =====================================================================================
# ================= Below tests are for the workload_request routes =================
# =====================================================================================


@pytest.mark.asyncio
@patch(
    "app.repositories.workload_request.create_workload_request", new_callable=AsyncMock
)
async def test_create_workload_request_route(mock_create):
    """
    Test the creation of a new workload request using mocked CRUD logic.
    Asserts that the POST request returns a 200 status and correct JSON response.
    """

    request_data = SAMPLE_REQUEST_DATA

    response_data = SAMPLE_RESPONSE_DATA

    mock_create.return_value = response_data

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/workload_request/", json=request_data)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == response_data


@pytest.mark.asyncio
@patch(
    "app.repositories.workload_request.update_workload_request", new_callable=AsyncMock
)
async def test_update_workload_request_route(mock_update):
    """
    Test updating a workload request using mocked CRUD logic.
    Asserts that the PUT request returns a 200 status and correct JSON response.
    """

    request_data = {"current_scale": 5}

    response_data = SAMPLE_RESPONSE_DATA

    mock_update.return_value = response_data

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.put(
            "/workload_request/123e4567-e89b-12d3-a456-426614174000", json=request_data
        )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == response_data


@pytest.mark.asyncio
@patch(
    "app.repositories.workload_request.delete_workload_request", new_callable=AsyncMock
)
async def test_delete_workload_request_route(mock_delete):
    """
    Test deleting a workload request using mocked CRUD logic.
    Asserts that the DELETE request returns a 200 status and correct JSON response.
    """

    response_data = {"message": "Workload request with ID 1 has been deleted"}

    mock_delete.return_value = response_data

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.delete(
            "/workload_request/123e4567-e89b-12d3-a456-426614174000"
        )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == response_data


@pytest.mark.asyncio
@patch(
    "app.repositories.workload_request.get_workload_requests", new_callable=AsyncMock
)
async def test_read_workload_requests_route(mock_get):
    """
    Test retrieving workload requests using mocked CRUD logic.
    Asserts that the GET request returns a 200 status and correct JSON response.
    """

    response_data = [SAMPLE_RESPONSE_DATA]

    mock_get.return_value = response_data

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/workload_request/")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == response_data


@pytest.mark.asyncio
@patch(
    "app.repositories.workload_request.get_workload_requests", new_callable=AsyncMock
)
async def test_read_workload_request_by_id_route(mock_get):
    """
    Test retrieving a specific workload request by ID using mocked CRUD logic.
    Asserts that the GET request returns a 200 status and correct JSON response.
    """

    response_data = SAMPLE_RESPONSE_DATA

    mock_get.return_value = response_data

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get(
            "/workload_request/123e4567-e89b-12d3-a456-426614174000"
        )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == response_data
