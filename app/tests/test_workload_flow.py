"""
Tests for get_workload_decision_action_flow.
"""

from operator import le
import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.exc import SQLAlchemyError

from app.repositories.workload_flow import get_workload_decision_action_flow
from app.models.workload_action import WorkloadAction
from app.models.workload_request_decision import WorkloadRequestDecision
from app.utils.exceptions import DatabaseConnectionException


@pytest.mark.asyncio
async def test_get_workload_decision_action_flow_success():
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
    db = AsyncMock()
    db.execute.side_effect = SQLAlchemyError("DB error")

    with pytest.raises(DatabaseConnectionException):
        await get_workload_decision_action_flow(
            db, pod_name="test-pod", namespace="test-ns"
        )
