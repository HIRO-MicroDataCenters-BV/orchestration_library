"""
Tests for the workload flow API.
This module tests the retrieval of workload decision action flows.
"""
from unittest.mock import AsyncMock, patch
import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest.mark.asyncio
@patch(
    "app.api.wrokload_flow_api.get_workload_decision_action_flow",
    new_callable=AsyncMock,
)
async def test_get_workload_flow_success(mock_get_flow):
    """Test successful retrieval of workload flow."""
    mock_get_flow.return_value = [
        {
            "pod_name": "pod1",
            "namespace": "default",
            "decision": "allow",
            "action": "bind",
        },
        {
            "pod_name": "pod2",
            "namespace": "default",
            "decision": "deny",
            "action": "delete",
        },
    ]
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/workload_flow/?pod_name=pod1&namespace=default")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data[0]["pod_name"] == "pod1"
    assert data[0]["decision"] == "allow"
    mock_get_flow.assert_awaited_once()


@pytest.mark.asyncio
@patch(
    "app.api.wrokload_flow_api.get_workload_decision_action_flow",
    new_callable=AsyncMock,
)
async def test_get_workload_flow_with_node_name(mock_get_flow):
    """Test retrieval with node_name filter."""
    mock_get_flow.return_value = [
        {
            "pod_name": "pod1",
            "namespace": "default",
            "node_name": "node1",
            "decision": "allow",
            "action": "bind",
        }
    ]
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get(
            "/workload_flow/?pod_name=pod1&namespace=default&node_name=node1"
        )
    assert response.status_code == 200
    data = response.json()
    assert data[0]["node_name"] == "node1"
    mock_get_flow.assert_awaited_once()


@pytest.mark.asyncio
@patch(
    "app.api.wrokload_flow_api.get_workload_decision_action_flow",
    new_callable=AsyncMock,
)
async def test_get_workload_flow_empty(mock_get_flow):
    """Test retrieval when no results are found."""
    mock_get_flow.return_value = []
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/workload_flow/?pod_name=podX&namespace=default")
    assert response.status_code == 200
    data = response.json()
    assert data == []
    mock_get_flow.assert_awaited_once()
