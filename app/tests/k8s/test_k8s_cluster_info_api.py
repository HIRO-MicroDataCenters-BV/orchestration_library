"""Test cases for the Kubernetes cluster info API endpoints."""
from unittest.mock import patch
import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.tests.utils.mock_objects import mock_cluster_info_api


@pytest.mark.asyncio
@patch("app.api.k8s.k8s_cluster_info.k8s_cluster_info.get_cluster_info")
async def test_get_advanced_cluster_info_route(mock_get_cluster_info):
    """Test getting advanced cluster info with query param."""
    data = mock_cluster_info_api()
    mock_get_cluster_info.return_value = data
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/k8s_cluster_info/?advanced=true")
    assert response.status_code == 200
    assert response.json() == data
    mock_get_cluster_info.assert_called_once()
