"""
Tests for tuning_parameter CRUD functions.
"""

import datetime
from unittest.mock import AsyncMock, MagicMock
import pytest
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.models.tuning_parameter import TuningParameter
from app.repositories import tuning_parameter
from app.schemas.tuning_parameter_schema import (
    TuningParameterBase,
    TuningParameterCreate,
    TuningParameterResponse,
)
from app.tests.utils.mock_objects import mock_metrics_details
from app.utils.exceptions import DatabaseConnectionException


def make_tuning_param(**kwargs):
    """Helper function to create a TuningParameter instance with default values."""
    defaults = {
        "id": 1,
        "output_1": 1.1,
        "output_2": 2.2,
        "output_3": 3.3,
        "alpha": 0.1,
        "beta": 0.2,
        "gamma": 0.3,
        "created_at": "2024-07-21T12:00:00Z",
    }
    defaults.update(kwargs)
    return TuningParameter(**defaults)


def test_get_parameters_returns_dict():
    """Test that get_parameters returns a dictionary of tuning parameters."""
    param = make_tuning_param()
    params = param.get_parameters()
    assert isinstance(params, dict)
    assert params["output_1"] == 1.1
    assert params["output_2"] == 2.2
    assert params["output_3"] == 3.3
    assert params["alpha"] == 0.1
    assert params["beta"] == 0.2
    assert params["gamma"] == 0.3


def test_repr_returns_string():
    """Test that __repr__ returns a string representation of the tuning parameter."""
    param = make_tuning_param()
    r = repr(param)
    assert r.startswith("<TuningParameter(")
    assert f"id={param.id}" in r
    assert f"created_at={param.created_at}" in r


def test_tuning_parameter_base_and_create():
    """Test TuningParameterBase and TuningParameterCreate schemas."""
    base = TuningParameterBase(
        output_1=1.0, output_2=2.0, output_3=3.0, alpha=0.1, beta=0.2, gamma=0.3
    )
    assert base.output_1 == 1.0
    create = TuningParameterCreate(**base.model_dump())
    assert create.alpha == 0.1
    assert isinstance(create, TuningParameterCreate)


def test_tuning_parameter_response_fields_and_config_methods():
    """Test TuningParameterResponse fields and config methods."""
    now = datetime.datetime.utcnow()
    resp = TuningParameterResponse(
        id=123,
        output_1=1.0,
        output_2=2.0,
        output_3=3.0,
        alpha=0.1,
        beta=0.2,
        gamma=0.3,
        created_at=now,
    )
    assert resp.id == 123
    assert resp.created_at == now
    # Test Config methods
    cfg = TuningParameterResponse.Config()
    assert cfg.get_orm_mode() is True
    cfg.set_orm_mode(False)
    assert cfg.get_orm_mode() is False


@pytest.mark.asyncio
async def test_create_tuning_parameters():
    """Test the creation of a new tuning parameter."""
    db = MagicMock()
    tuning_parameter_create = TuningParameterCreate(
        output_1=1.0, output_2=1.0, output_3=1.0, alpha=1.0, beta=1.0, gamma=1.0
    )
    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    result = await tuning_parameter.create_tuning_parameter(
        db,
        tuning_parameter_create,
        metrics_details=mock_metrics_details("POST", "/tuning_parameters"),
    )
    db.add.assert_called_once()
    db.commit.assert_called_once()
    db.refresh.assert_called_once()
    assert isinstance(result, TuningParameter)


@pytest.mark.asyncio
async def test_get_tuning_parameters():
    """Test retrieving tuning parameters."""
    mock = MagicMock(spec=TuningParameter)
    mock.id = 1
    mock.output_1 = 1.0
    mock.output_2 = 1.0
    mock.output_3 = 1.0
    mock.alpha = 1.0
    mock.beta = 1.0
    mock.gamma = 1.0

    mock_scalars = MagicMock()
    mock_scalars.all.return_value = [mock]

    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars

    db = AsyncMock()
    db.execute.return_value = mock_result

    result = await tuning_parameter.get_tuning_parameters(
        db, metrics_details=mock_metrics_details("GET", "/tuning_parameters")
    )

    db.execute.assert_called_once()
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0].id == 1
    assert result[0].output_1 == 1.0


@pytest.mark.asyncio
async def test_get_latest_tuning_parameters():
    """Test retrieving the latest tuning parameters."""
    mock_param = MagicMock(spec=TuningParameter)
    mock_param.id = 2.0
    mock_param.output_1 = 2.0
    mock_param.output_2 = 2.0
    mock_param.output_3 = 2.0
    mock_param.alpha = 2.0
    mock_param.beta = 2.0
    mock_param.gamma = 2.0

    mock_scalars = MagicMock()
    mock_scalars.all.return_value = [mock_param]

    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars

    db = AsyncMock()
    db.execute.return_value = mock_result

    result = await tuning_parameter.get_latest_tuning_parameters(
        db
    )

    db.execute.assert_called_once()
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0].id == 2.0
    assert result[0].output_1 == 2.0


@pytest.mark.asyncio
async def test_get_tuning_parameters_empty():
    """Test retrieving tuning parameters when no records exist."""
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = []

    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars

    db = AsyncMock()
    db.execute.return_value = mock_result

    result = await tuning_parameter.get_tuning_parameters(
        db, metrics_details=mock_metrics_details("GET", "/tuning_parameters")
    )

    db.execute.assert_called_once()
    assert isinstance(result, list)
    assert len(result) == 0


@pytest.mark.asyncio
async def test_get_tuning_parameters_with_start_date():
    """Test retrieving tuning parameters with start_date filter."""
    mock = MagicMock(spec=TuningParameter)
    mock.id = 1

    mock_scalars = MagicMock()
    mock_scalars.all.return_value = [mock]

    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars

    db = AsyncMock()
    db.execute.return_value = mock_result

    start_date = datetime.datetime(2024, 1, 1, tzinfo=datetime.timezone.utc)
    result = await tuning_parameter.get_tuning_parameters(
        db,
        tuning_parameter_reqest_args={"start_date": start_date},
        metrics_details=mock_metrics_details("GET", "/tuning_parameters"),
    )

    db.execute.assert_called_once()
    assert isinstance(result, list)
    assert result[0].id == 1


@pytest.mark.asyncio
async def test_get_tuning_parameters_with_end_date():
    """Test retrieving tuning parameters with end_date filter."""
    mock = MagicMock(spec=TuningParameter)
    mock.id = 2

    mock_scalars = MagicMock()
    mock_scalars.all.return_value = [mock]

    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars

    db = AsyncMock()
    db.execute.return_value = mock_result

    end_date = datetime.datetime(2025, 1, 1, tzinfo=datetime.timezone.utc)
    result = await tuning_parameter.get_tuning_parameters(
        db,
        tuning_parameter_reqest_args={"end_date": end_date},
        metrics_details=mock_metrics_details("GET", "/tuning_parameters"),
    )

    db.execute.assert_called_once()
    assert isinstance(result, list)
    assert result[0].id == 2


@pytest.mark.asyncio
async def test_get_tuning_parameters_with_start_and_end_date():
    """Test retrieving tuning parameters with both start_date and end_date filters."""
    mock = MagicMock(spec=TuningParameter)
    mock.id = 3

    mock_scalars = MagicMock()
    mock_scalars.all.return_value = [mock]

    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars

    db = AsyncMock()
    db.execute.return_value = mock_result

    start_date = datetime.datetime(2024, 1, 1, tzinfo=datetime.timezone.utc)
    end_date = datetime.datetime(2025, 1, 1, tzinfo=datetime.timezone.utc)
    result = await tuning_parameter.get_tuning_parameters(
        db,
        tuning_parameter_reqest_args={"start_date": start_date, "end_date": end_date},
        metrics_details=mock_metrics_details("GET", "/tuning_parameters"),
    )

    db.execute.assert_called_once()
    assert isinstance(result, list)
    assert result[0].id == 3


@pytest.mark.asyncio
async def test_create_tuning_parameter_integrity_error():
    """Test creating a tuning parameter with integrity error."""
    db = AsyncMock()
    db.add = MagicMock()
    db.commit = AsyncMock(side_effect=IntegrityError("stmt", "params", "orig"))
    db.refresh = AsyncMock()
    db.rollback = AsyncMock()
    param = TuningParameterCreate(
        output_1=1, output_2=1, output_3=1, alpha=1, beta=1, gamma=1
    )
    with pytest.raises(DatabaseConnectionException) as exc:
        await tuning_parameter.create_tuning_parameter(
            db,
            param,
            metrics_details=mock_metrics_details("POST", "/tuning_parameters"),
        )
    db.rollback.assert_awaited()
    assert "Invalid tuning parameter data" in str(exc.value)


@pytest.mark.asyncio
async def test_create_tuning_parameter_sqlalchemy_error():
    """Test creating a tuning parameter with SQLAlchemy error."""
    db = AsyncMock()
    db.add = MagicMock()
    db.commit = AsyncMock(side_effect=SQLAlchemyError("db error"))
    db.refresh = AsyncMock()
    db.rollback = AsyncMock()
    param = TuningParameterCreate(
        output_1=1, output_2=1, output_3=1, alpha=1, beta=1, gamma=1
    )
    with pytest.raises(DatabaseConnectionException) as exc:
        await tuning_parameter.create_tuning_parameter(
            db,
            param,
            metrics_details=mock_metrics_details("POST", "/tuning_parameters"),
        )
    db.rollback.assert_awaited()
    assert "Failed to create tuning parameter" in str(exc.value)


@pytest.mark.asyncio
async def test_create_tuning_parameter_unexpected_error():
    """Test creating a tuning parameter with an unexpected error."""
    db = AsyncMock()
    db.add = MagicMock()
    db.commit = AsyncMock(side_effect=Exception("unexpected"))
    db.refresh = AsyncMock()
    db.rollback = AsyncMock()
    param = TuningParameterCreate(
        output_1=1, output_2=1, output_3=1, alpha=1, beta=1, gamma=1
    )
    with pytest.raises(DatabaseConnectionException) as exc:
        await tuning_parameter.create_tuning_parameter(
            db,
            param,
            metrics_details=mock_metrics_details("POST", "/tuning_parameters"),
        )
    db.rollback.assert_awaited()
    assert "An unexpected error occurred" in str(exc.value)


@pytest.mark.asyncio
async def test_get_tuning_parameters_sqlalchemy_error():
    """Test retrieving tuning parameters with SQLAlchemy error."""
    db = AsyncMock()
    db.execute = AsyncMock(side_effect=SQLAlchemyError("db error"))
    with pytest.raises(DatabaseConnectionException) as exc:
        await tuning_parameter.get_tuning_parameters(
            db, metrics_details=mock_metrics_details("GET", "/tuning_parameters")
        )
    assert "Failed to retrieve tuning parameters" in str(exc.value)


@pytest.mark.asyncio
async def test_get_tuning_parameters_unexpected_error():
    """Test retrieving tuning parameters with an unexpected error."""
    db = AsyncMock()
    db.execute = AsyncMock(side_effect=Exception("unexpected"))
    with pytest.raises(DatabaseConnectionException) as exc:
        await tuning_parameter.get_tuning_parameters(
            db, metrics_details=mock_metrics_details("GET", "/tuning_parameters")
        )
    assert "An unexpected error occurred" in str(exc.value)


@pytest.mark.asyncio
async def test_get_latest_tuning_parameters_not_found():
    """Test retrieving latest tuning parameters when none exist."""
    db = AsyncMock()
    mock_result = MagicMock()
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = []
    mock_result.scalars.return_value = mock_scalars
    db.execute.return_value = mock_result
    with pytest.raises(DatabaseConnectionException):
        await tuning_parameter.get_latest_tuning_parameters(
            db, metrics_details=mock_metrics_details("GET", "/tuning_parameters")
        )


@pytest.mark.asyncio
async def test_get_latest_tuning_parameters_sqlalchemy_error():
    """Test retrieving latest tuning parameters with SQLAlchemy error."""
    db = AsyncMock()
    db.execute = AsyncMock(side_effect=SQLAlchemyError("db error"))
    with pytest.raises(DatabaseConnectionException) as exc:
        await tuning_parameter.get_latest_tuning_parameters(
            db, metrics_details=mock_metrics_details("GET", "/tuning_parameters")
        )
    assert "Failed to retrieve latest tuning parameters" in str(exc.value)


@pytest.mark.asyncio
async def test_get_latest_tuning_parameters_unexpected_error():
    """Test retrieving latest tuning parameters with an unexpected error."""
    db = AsyncMock()
    db.execute = AsyncMock(side_effect=Exception("unexpected"))
    with pytest.raises(DatabaseConnectionException) as exc:
        await tuning_parameter.get_latest_tuning_parameters(
            db, metrics_details=mock_metrics_details("GET", "/tuning_parameters")
        )
    assert "An unexpected error occurred" in str(exc.value)
