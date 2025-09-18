"""
Tests for get_workload_decision_action_flow.
"""

from unittest.mock import AsyncMock, MagicMock
import pytest
from sqlalchemy.exc import SQLAlchemyError

from app.repositories.workload_decision_action_flow import (
    get_workload_decision_action_flow,
)
from app.tests.utils.mock_objects import mock_workload_decision_action_flow_item
from app.utils.constants import WorkloadActionTypeEnum
from app.utils.exceptions import DatabaseConnectionException


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "pod_name,namespace,node_name,action_type",
    [
        ("test-pod-bind", "test-ns", "test-node", WorkloadActionTypeEnum.BIND),
        ("test-pod-create", "test-ns", "test-node", WorkloadActionTypeEnum.CREATE),
        ("test-pod-delete", "test-ns", "test-node", WorkloadActionTypeEnum.DELETE),
        ("test-pod-move", "test-ns", "test-node", WorkloadActionTypeEnum.MOVE),
        ("test-pod-swapx", "test-ns", "test-node", WorkloadActionTypeEnum.SWAP_X),
        ("test-pod-swapy", "test-ns", "test-node", WorkloadActionTypeEnum.SWAP_Y),
    ],
)
async def test_get_workload_decision_action_flow_success(
    pod_name, namespace, node_name, action_type
):
    """Test for successful retrieval of workload decision and action flow."""
    # Mock database session
    db = AsyncMock()

    # Mock objects
    mock_item = mock_workload_decision_action_flow_item(
        pod_name=pod_name,
        namespace=namespace,
        node_name=node_name,
        action_type=action_type,
    )

    # Mock result.all() to return a list of tuples
    mock_result = MagicMock()
    mock_result.all.return_value = [mock_item]
    mock_result.scalars.return_value.all.return_value = [mock_item]
    db.execute.return_value = mock_result

    # Call the function
    result = await get_workload_decision_action_flow(
        db,
        flow_filters={
            "pod_name": pod_name,
            "namespace": namespace,
            "node_name": node_name,
            "action_type": action_type,
        },
    )

    db.execute.assert_called_once()
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0].decision_pod_name == pod_name
    assert result[0].decision_namespace == namespace
    assert result[0].decision_node_name == node_name
    assert result[0].action_type == action_type


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "pod_name,namespace,node_name,action_type",
    [
        ("notfound", "test-ns", "test-node", "bind"),
        (None, None, None, None),
    ],
)
async def test_get_workload_decision_action_flow_empty(
    pod_name, namespace, node_name, action_type
):
    """Test for empty result when no matching workload actions found."""
    db = AsyncMock()
    mock_result = MagicMock()
    mock_result.all.return_value = []
    mock_result.scalars.return_value.all.return_value = []
    db.execute.return_value = mock_result

    result = await get_workload_decision_action_flow(
        db,
        flow_filters={
            "pod_name": pod_name,
            "namespace": namespace,
            "node_name": node_name,
            "action_type": action_type,
        },
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
            db,
            flow_filters={
                "pod_name": "test-pod",
                "namespace": "test-ns",
                "node_name": "test-node",
                "action_type": "bind",
            },
        )
