"""Test cases for the Kubernetes node API endpoints."""
from unittest.mock import patch
import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.tests.utils.mock_objects import mock_node, mock_to_dict

@pytest.mark.asyncio
@patch("app.api.k8s.k8s_node.k8s_node.list_k8s_nodes")
async def test_list_all_nodes_default(mock_list_k8s_nodes):
    """Test listing all nodes with no filters."""
    mock_response = [mock_to_dict(mock_node())]   # Mock response with a single node
    mock_list_k8s_nodes.return_value = mock_response
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/k8s_node/")
    assert response.status_code == 200
    assert response.json() == mock_response
    mock_list_k8s_nodes.assert_called_once()
