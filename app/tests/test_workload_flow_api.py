"""
Tests for the workload flow API.
This module tests the retrieval of workload decision action flows.
"""

from unittest.mock import AsyncMock, patch
from uuid import uuid4
import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.tests.utils.mock_objects import mock_workload_decision_action_flow_data
from app.utils.constants import WorkloadActionTypeEnum


@pytest.mark.asyncio
@patch(
    "app.api.workload_decision_action_flow_api.get_workload_decision_action_flow",
    new_callable=AsyncMock,
)
async def test_get_workload_flow_success(mock_get_flow):
    """Test successful retrieval of workload flow."""
    mock_get_flow.return_value = [
        mock_workload_decision_action_flow_data(
            flow_filters={
                "decision_id": uuid4(),
                "action_id": uuid4(),
                "pod_name": "pod1",
                "namespace": "default",
                "node_name": "node1",
                "action_type": WorkloadActionTypeEnum.BIND,
            }
        ),
        mock_workload_decision_action_flow_data(
            flow_filters={
                "decision_id": uuid4(),
                "action_id": uuid4(),
                "pod_name": "pod2",
                "namespace": "default",
                "node_name": "node2",
                "action_type": WorkloadActionTypeEnum.DELETE,
            }
        ),
    ]

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/workload_decision_action_flow/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data[0]["decision_pod_name"] == "pod1"
    assert data[0]["decision_status"] == "succeeded"
    assert data[0]["action_type"] == "bind"
    assert data[1]["decision_pod_name"] == "pod2"
    assert data[1]["decision_status"] == "succeeded"
    assert data[1]["action_type"] == "delete"
    mock_get_flow.assert_awaited_once()


@pytest.mark.asyncio
@patch(
    "app.api.workload_decision_action_flow_api.get_workload_decision_action_flow",
    new_callable=AsyncMock,
)
async def test_get_workload_flow_with_node_name(mock_get_flow):
    """Test retrieval with node_name filter."""
    decision_id = uuid4()
    action_id = uuid4()
    mock_get_flow.return_value = [
        mock_workload_decision_action_flow_data(
            flow_filters={
                "decision_id": decision_id,
                "action_id": action_id,
                "pod_name": "pod1",
                "namespace": "default",
                "node_name": "node1",
                "action_type": WorkloadActionTypeEnum.BIND,
            }
        )
    ]
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get(
            f"/workload_decision_action_flow/?decision_id={decision_id}"
            f"&action_id={action_id}"
            "&pod_name=pod1"
            "&namespace=default"
            "&node_name=node1"
            "&action_type=bind"
        )
    assert response.status_code == 200
    data = response.json()
    assert data[0]["decision_node_name"] == "node1"
    assert data[0]["decision_pod_name"] == "pod1"
    assert data[0]["decision_status"] == "succeeded"
    assert data[0]["action_type"] == "bind"
    mock_get_flow.assert_awaited_once()


@pytest.mark.asyncio
@patch(
    "app.api.workload_decision_action_flow_api.get_workload_decision_action_flow",
    new_callable=AsyncMock,
)
async def test_get_workload_flow_empty(mock_get_flow):
    """Test retrieval when no results are found."""
    mock_get_flow.return_value = []
    decision_id = uuid4()
    action_id = uuid4()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get(
            f"/workload_decision_action_flow/?decision_id={decision_id}"
            f"&action_id={action_id}"
            "&pod_name=podX"
            "&namespace=default"
            "&node_name=nodeX"
            "&action_type=bind"
        )
    assert response.status_code == 200
    data = response.json()
    assert data == []
    mock_get_flow.assert_awaited_once()
