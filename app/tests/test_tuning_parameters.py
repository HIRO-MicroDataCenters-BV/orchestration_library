"""
Tests for tuning_parameter CRUD functions.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.tuning_parameter import TuningParameter
from app.repositories import tuning_parameter
from app.schemas.tuning_parameter_schema import TuningParameterCreate


@pytest.mark.asyncio
async def test_create_tuning_parameters():
    """Test the creation of a new tuning parameter."""
    db = MagicMock()
    tuning_parameter_create = TuningParameterCreate(
        output_1=1.0,
        output_2=1.0,
        output_3=1.0,
        alpha=1.0,
        beta=1.0,
        gamma=1.0
    )
    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    result = await tuning_parameter.create_tuning_parameter(db, tuning_parameter_create)
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

    result = await tuning_parameter.get_tuning_parameters(db)

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

    result = await tuning_parameter.get_latest_tuning_parameters(db)

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

    result = await tuning_parameter.get_tuning_parameters(db)

    db.execute.assert_called_once()
    assert isinstance(result, list)
    assert len(result) == 0
