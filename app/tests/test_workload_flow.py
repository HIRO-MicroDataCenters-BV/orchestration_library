"""
Tests for get_workload_decision_action_flow.
"""

from unittest.mock import AsyncMock, MagicMock
import pytest
from sqlalchemy.exc import SQLAlchemyError

from app.repositories.workload_flow import get_workload_decision_action_flow
from app.models.workload_action import WorkloadAction
from app.models.workload_request_decision import WorkloadRequestDecision
from app.utils.exceptions import DatabaseConnectionException


@pytest.mark.asyncio
async def test_get_workload_decision_action_flow_success():
    """Test for successful retrieval of workload decision and action flow."""
    # Mock database session
    db = AsyncMock()

    # Mock objects
    mock_decision = MagicMock(spec=WorkloadRequestDecision)
    mock_action = MagicMock(spec=WorkloadAction)
    mock_row = (mock_decision, mock_action)

    # Mock result.all() to return a list of tuples
    mock_result = MagicMock()
    mock_result.all.return_value = [mock_row]
    mock_result.scalars.return_value.all.return_value = [mock_row]
    db.execute.return_value = mock_result

    # Call the function
    result = await get_workload_decision_action_flow(
        db, pod_name="test-pod", namespace="test-ns", node_name="test-node"
    )

    db.execute.assert_called_once()
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["decision"] == mock_decision
    assert result[0]["action"] == mock_action


@pytest.mark.asyncio
async def test_get_workload_decision_action_flow_empty():
    """Test for empty result when no matching workload actions found."""
    db = AsyncMock()
    mock_result = MagicMock()
    mock_result.all.return_value = []
    db.execute.return_value = mock_result

    result = await get_workload_decision_action_flow(
        db, pod_name="notfound", namespace="test-ns"
    )
    db.execute.assert_called_once()
    assert result == []


@pytest.mark.asyncio
async def test_get_workload_decision_action_flow_db_error():
    """Test for handling database connection errors."""
    db = AsyncMock()
    db.execute.side_effect = SQLAlchemyError("DB error")

    with pytest.raises(DatabaseConnectionException):
        await get_workload_decision_action_flow(
            db, pod_name="test-pod", namespace="test-ns"
        )
