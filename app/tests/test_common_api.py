"""Common API endpoints for managing pods and workload requests."""
from unittest.mock import patch
import pytest
from httpx import ASGITransport, AsyncClient
from uuid import UUID

from app.main import app

@pytest.mark.asyncio
@patch("app.repositories.pod.workload_request_ids_per_node")
async def test_get_workloads_per_pod(mock_workload_request_ids_per_node):
    """
    Test the get_workloads_per_pod route.
    This test mocks the database call to return a predefined list of workload request IDs
    for a given node ID and checks if the API returns the expected response.
    """
    node_id = UUID("c7e1f2a3-8b4d-4e2a-9c7b-1f5e3d2a8b6c")
    expected_ids = [
        UUID("e2b7c7e6-1a8a-4e3d-9a7e-2f8e2c7b8e1f"),
        UUID("a3d5f9b2-4c6e-4f1a-9b2e-7c8d1e5a2f3b"),
    ]
    mock_workload_request_ids_per_node.return_value = expected_ids

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get(f"/workload_request_per_node/{node_id}")

    assert response.status_code == 200
    assert response.json() == [str(uid) for uid in expected_ids]