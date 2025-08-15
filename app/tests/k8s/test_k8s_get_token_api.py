"""Test cases for the Kubernetes get token API endpoints."""
from unittest.mock import patch
import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app

@pytest.mark.asyncio
@patch("app.api.k8s.k8s_get_token_api.k8s_get_token.get_read_only_token")
async def test_get_ro_token_default(mock_get_read_only_token):
    """Test getting read-only token with default namespace and service account."""
    mock_response = {"token": "mocked-token"}
    mock_get_read_only_token.return_value = mock_response
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/k8s_get_token/")
    assert response.status_code == 200
    assert response.json() == mock_response
    mock_get_read_only_token.assert_called_once()

@pytest.mark.asyncio
@patch("app.api.k8s.k8s_get_token_api.k8s_get_token.get_read_only_token")
async def test_get_ro_token_returns_error(mock_get_read_only_token):
    """Test getting read-only token when API returns an error."""
    mock_response = {"error": "Service account not found"}
    mock_get_read_only_token.return_value = mock_response
    params = {"namespace": "bad-ns", "service_account_name": "bad-sa"}
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/k8s_get_token/", params=params)
    assert response.status_code == 200
    assert response.json() == mock_response
    mock_get_read_only_token.assert_called_once()