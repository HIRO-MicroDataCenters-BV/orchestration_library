"""
Tests for tuning_parameter_apis CRUD functions.
"""

import pytest
from unittest.mock import AsyncMock, patch, ANY
from datetime import datetime

from httpx import ASGITransport, AsyncClient
from starlette import status

from app.main import app

# Sample test data
SAMPLE_TUNING_PARAM = {
    "id": 1,
    "output_1": 1.0,
    "output_2": 2.0,
    "output_3": 3.0,
    "alpha": 0.1,
    "beta": 0.2,
    "gamma": 0.3,
    "created_at": datetime.utcnow().isoformat(),
}


@pytest.fixture
def mock_db():
    """Fixture for database session mock."""
    return AsyncMock()


@pytest.mark.asyncio
@patch("app.repositories.tuning_parameter.create_tuning_parameter", new_callable=AsyncMock)
async def test_create_tuning_parameters_success(mock_create):
    """Test successful creation of tuning parameters."""
    request_data = {
        "output_1": 1.0,
        "output_2": 2.0,
        "output_3": 3.0,
        "alpha": 0.1,
        "beta": 0.2,
        "gamma": 0.3,
    }
    mock_create.return_value = SAMPLE_TUNING_PARAM

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/tuning_parameters/", json=request_data)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == SAMPLE_TUNING_PARAM
    mock_create.assert_called_once()


@pytest.mark.asyncio
@patch("app.repositories.tuning_parameter.create_tuning_parameter", new_callable=AsyncMock)
async def test_create_tuning_parameters_validation_error(mock_create):
    """Test creation of tuning parameters with invalid data."""
    invalid_data = {
        "output_1": "invalid",  # Should be float
        "output_2": 2.0,
        "output_3": 3.0,
        "alpha": 0.1,
        "beta": 0.2,
        "gamma": 0.3,
    }

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/tuning_parameters/", json=invalid_data)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    mock_create.assert_not_called()


@pytest.mark.asyncio
@patch("app.repositories.tuning_parameter.get_latest_tuning_parameters", new_callable=AsyncMock)
async def test_get_latest_tuning_parameter_success(mock_get_latest):
    """Test successful retrieval of latest tuning parameter."""
    mock_get_latest.return_value = [SAMPLE_TUNING_PARAM]

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/tuning_parameters/latest/1")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [SAMPLE_TUNING_PARAM]  # Expecting a list with one item
    mock_get_latest.assert_called_once_with(ANY, limit=1)  # ANY for db session


@pytest.mark.asyncio
@patch("app.repositories.tuning_parameter.get_latest_tuning_parameters", new_callable=AsyncMock)
async def test_get_latest_tuning_parameter_not_found(mock_get_latest):
    """Test retrieval of latest tuning parameter when none exist."""

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/tuning_parameters/latest/1")

    assert response.status_code == status.HTTP_200_OK
    mock_get_latest.assert_called_once_with(ANY, limit=1)  # ANY for db session


@pytest.mark.asyncio
@patch("app.repositories.tuning_parameter.get_tuning_parameters", new_callable=AsyncMock)
async def test_get_all_tuning_parameters_success(mock_get_all):
    """Test successful retrieval of all tuning parameters."""
    mock_get_all.return_value = [SAMPLE_TUNING_PARAM]

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/tuning_parameters/")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [SAMPLE_TUNING_PARAM]
    mock_get_all.assert_called_once()


@pytest.mark.asyncio
@patch("app.repositories.tuning_parameter.get_tuning_parameters", new_callable=AsyncMock)
async def test_get_tuning_parameters_with_filters(mock_get_all):
    """Test retrieval of tuning parameters with date filters."""
    mock_get_all.return_value = [SAMPLE_TUNING_PARAM]
    start_date = "2024-01-01T00:00:00"
    end_date = "2024-12-31T23:59:59"

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get(
            f"/tuning_parameters/?start_date={start_date}&end_date={end_date}"
        )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [SAMPLE_TUNING_PARAM]
    mock_get_all.assert_called_once()
