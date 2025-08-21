"""Test cases for the Kubernetes pod API endpoints."""
from unittest.mock import patch
import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.tests.utils.mock_objects import mock_pod, mock_to_dict, mock_user_pod

@pytest.mark.asyncio
@patch("app.api.k8s.k8s_pod.k8s_pod.list_k8s_pods")
async def test_list_all_pods_default(mock_list_k8s_pods):
    """Test listing all pods with no filters."""
    mock_response = [mock_to_dict(mock_pod())]
    mock_list_k8s_pods.return_value = mock_response
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/k8s_pod/")
    assert response.status_code == 200
    assert response.json() == mock_response
    mock_list_k8s_pods.assert_called_once()

@pytest.mark.asyncio
@patch("app.api.k8s.k8s_user_pod.k8s_pod.list_k8s_user_pods")
async def test_list_all_user_pods_default(mock_list_k8s_user_pods):
    """Test listing all user pods with no filters."""
    mock_response = [mock_to_dict(mock_user_pod())]
    mock_list_k8s_user_pods.return_value = mock_response
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/k8s_user_pod/")
    assert response.status_code == 200
    assert response.json() == mock_response
    mock_list_k8s_user_pods.assert_called_once()
