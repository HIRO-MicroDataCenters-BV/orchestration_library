"""Test cases for the Kubernetes pod parent API endpoint."""
from unittest.mock import patch
import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app

@pytest.mark.asyncio
@patch("app.api.k8s.k8s_pod_parent.k8s_pod_parent.get_parent_controller_details_of_pod")
async def test_get_pod_parent_with_name(mock_get_parent_controller):
    """Test getting pod parent by namespace and name."""
    mock_response = {"kind": "Deployment", "name": "my-deployment"}
    mock_get_parent_controller.return_value = mock_response
    params = {"namespace": "default", "name": "mypod"}
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/k8s_pod_parent/", params=params)
    assert response.status_code == 200
    assert response.json() == mock_response
    mock_get_parent_controller.assert_called_once()
