import pytest
from unittest.mock import patch, MagicMock
from fastapi.responses import JSONResponse
from kubernetes.client.rest import ApiException
from kubernetes.config.config_exception import ConfigException
from app.repositories.k8s import k8s_get_token

def test_get_read_only_token_missing_params():
    """Should return 400 if namespace or service_account_name is missing."""
    resp = k8s_get_token.get_read_only_token(namespace=None, service_account_name=None)
    assert isinstance(resp, JSONResponse)
    assert resp.status_code == 400
    assert "must be provided" in resp.body.decode()

@patch("app.repositories.k8s.k8s_get_token.create_token_for_sa")
def test_get_read_only_token_success(mock_create_token):
    """Should return token in JSONResponse on success."""
    mock_create_token.return_value = "dummy-token"
    resp = k8s_get_token.get_read_only_token(namespace="ns", service_account_name="sa")
    assert resp.status_code == 200
    assert "dummy-token" in resp.body.decode()

@patch("app.repositories.k8s.k8s_get_token.create_token_for_sa")
@patch("app.repositories.k8s.k8s_get_token.handle_k8s_exceptions")
def test_get_read_only_token_api_exception(mock_handle, mock_create_token):
    """Should call handle_k8s_exceptions on ApiException."""
    mock_create_token.side_effect = ApiException("api error")
    k8s_get_token.get_read_only_token(namespace="ns", service_account_name="sa")
    mock_handle.assert_called_once()
    assert "Kubernetes API error" in mock_handle.call_args[1]["context_msg"]

@patch("app.repositories.k8s.k8s_get_token.create_token_for_sa")
@patch("app.repositories.k8s.k8s_get_token.handle_k8s_exceptions")
def test_get_read_only_token_config_exception(mock_handle, mock_create_token):
    """Should call handle_k8s_exceptions on ConfigException."""
    mock_create_token.side_effect = ConfigException("config error")
    k8s_get_token.get_read_only_token(namespace="ns", service_account_name="sa")
    mock_handle.assert_called_once()
    assert "Kubernetes configuration error" in mock_handle.call_args[1]["context_msg"]

@patch("app.repositories.k8s.k8s_get_token.create_token_for_sa")
@patch("app.repositories.k8s.k8s_get_token.handle_k8s_exceptions")
def test_get_read_only_token_value_error(mock_handle, mock_create_token):
    """Should call handle_k8s_exceptions on ValueError."""
    mock_create_token.side_effect = ValueError("bad value")
    k8s_get_token.get_read_only_token(namespace="ns", service_account_name="sa")
    mock_handle.assert_called_once()
    assert "Value error" in mock_handle.call_args[1]["context_msg"]

@patch("app.repositories.k8s.k8s_get_token.get_k8s_core_v1_client")
def test_create_token_for_sa_success(mock_get_core):
    """Should return token string from token_response."""
    mock_core = MagicMock()
    mock_token_response = MagicMock()
    mock_token_response.status.token = "real-token"
    mock_core.create_namespaced_service_account_token.return_value = mock_token_response
    mock_get_core.return_value = mock_core

    token = k8s_get_token.create_token_for_sa("ns", "sa")
    assert token == "real-token"