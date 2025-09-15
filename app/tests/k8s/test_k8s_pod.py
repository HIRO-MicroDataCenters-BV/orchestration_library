"""
Tests for CRUD operations and routes related to K8S Pod management.
"""

from unittest.mock import MagicMock, patch

import json

import pytest
from kubernetes.config.config_exception import ConfigException
from kubernetes.client.rest import ApiException
from app.utils.exceptions import K8sAPIException, K8sConfigException, K8sValueError

from app.repositories.k8s import k8s_pod
from app.tests.utils.mock_objects import mock_metrics_details, pod_mock_fixture


@patch("app.repositories.k8s.k8s_pod.get_k8s_core_v1_client")
def test_list_k8s_pods_all_namespaces(mock_get_client):
    """
    Test listing all pods in all namespaces.
    """
    mock_core_v1 = MagicMock()
    mock_core_v1.list_pod_for_all_namespaces.return_value.items = [pod_mock_fixture()]
    mock_get_client.return_value = mock_core_v1

    response = k8s_pod.list_k8s_pods()
    assert response.status_code == 200

    pods = json.loads(response.body)
    assert len(pods) == 1
    assert pods[0]["name"] == "test-pod"
    assert pods[0]["namespace"] == "default"


@patch("app.repositories.k8s.k8s_pod.get_k8s_core_v1_client")
def test_list_k8s_pods_with_namespace(mock_get_client):
    """
    Test listing pods in a specific namespace.
    """
    mock_core_v1 = MagicMock()
    mock_core_v1.list_namespaced_pod.return_value.items = [pod_mock_fixture()]
    mock_get_client.return_value = mock_core_v1

    pod_filters = {
        "namespace": "default",
    }
    metrics_details = mock_metrics_details("GET", "/k8s_pod")
    response = k8s_pod.list_k8s_pods(
        pod_filters=pod_filters, metrics_details=metrics_details
    )
    assert response.status_code == 200
    pods = json.loads(response.body)
    assert pods[0]["namespace"] == "default"


def setup_pod_mocks(mock_get_client, mock_get_pod_details):
    """Helper function to set up mock pods for testing."""
    pod1 = MagicMock()
    pod1.metadata.name = "test-pod"
    pod1.metadata.uid = "123e4567-e89b-12d3-a456-426614174000"
    pod1.metadata.namespace = "default"
    pod1.status.phase = "Running"

    pod2 = MagicMock()
    pod2.metadata.name = "other-pod"
    pod2.metadata.uid = "123e4567-e89b-12d3-a456-426614174001"
    pod2.metadata.namespace = "kube-system"
    pod2.status.phase = "Failed"

    mock_core_v1 = MagicMock()
    mock_core_v1.list_pod_for_all_namespaces.return_value.items = [pod1, pod2]
    mock_core_v1.list_namespaced_pod.return_value.items = [pod1]
    mock_get_client.return_value = mock_core_v1

    mock_get_pod_details.side_effect = lambda pod: {
        "name": pod.metadata.name,
        "namespace": pod.metadata.namespace,
    }


@patch("app.repositories.k8s.k8s_pod.get_pod_details")
@patch("app.repositories.k8s.k8s_pod.get_k8s_core_v1_client")
def test_list_k8s_pods_filter_by_name(mock_get_client, mock_get_pod_details):
    """Test listing pods filtered by name."""
    setup_pod_mocks(mock_get_client, mock_get_pod_details)

    pod_filters = {
        "name": "test-pod",
    }
    metrics_details = mock_metrics_details("GET", "/k8s_pod")
    response = k8s_pod.list_k8s_pods(
        pod_filters=pod_filters, metrics_details=metrics_details
    )
    pods = json.loads(response.body)
    assert len(pods) == 1
    assert pods[0]["name"] == "test-pod"

    response = k8s_pod.list_k8s_pods(
        pod_filters={"name": "does-not-exist"}, metrics_details=metrics_details
    )
    pods = json.loads(response.body)
    assert len(pods) == 0


@patch("app.repositories.k8s.k8s_pod.get_pod_details")
@patch("app.repositories.k8s.k8s_pod.get_k8s_core_v1_client")
def test_list_k8s_pods_filter_by_pod_id(mock_get_client, mock_get_pod_details):
    """Test listing pods filtered by pod ID."""
    setup_pod_mocks(mock_get_client, mock_get_pod_details)
    pod_filters = {
        "pod_id": "123e4567-e89b-12d3-a456-426614174000",
    }
    metrics_details = mock_metrics_details("GET", "/k8s_pod")
    response = k8s_pod.list_k8s_pods(
        pod_filters=pod_filters, metrics_details=metrics_details
    )
    pods = json.loads(response.body)
    assert len(pods) == 1
    assert pods[0]["name"] == "test-pod"

    response = k8s_pod.list_k8s_pods(
        pod_filters={"pod_id": "no-such-uid"}, metrics_details=metrics_details
    )
    pods = json.loads(response.body)
    assert len(pods) == 0


@patch("app.repositories.k8s.k8s_pod.get_pod_details")
@patch("app.repositories.k8s.k8s_pod.get_k8s_core_v1_client")
def test_list_k8s_pods_filter_by_status(mock_get_client, mock_get_pod_details):
    """Test listing pods filtered by status."""
    setup_pod_mocks(mock_get_client, mock_get_pod_details)
    pod_filters = {
        "status": "Running",
    }
    metrics_details = mock_metrics_details("GET", "/k8s_pod")
    response = k8s_pod.list_k8s_pods(
        pod_filters=pod_filters, metrics_details=metrics_details
    )
    pods = json.loads(response.body)
    assert len(pods) == 1
    assert pods[0]["name"] == "test-pod"

    response = k8s_pod.list_k8s_pods(
        pod_filters={"status": "Pending"}, metrics_details=metrics_details
    )
    pods = json.loads(response.body)
    assert len(pods) == 0


@patch("app.repositories.k8s.k8s_pod.get_pod_details")
@patch("app.repositories.k8s.k8s_pod.get_k8s_core_v1_client")
def test_list_k8s_pods_filter_by_namespace(mock_get_client, mock_get_pod_details):
    """Test listing pods filtered by namespace."""
    setup_pod_mocks(mock_get_client, mock_get_pod_details)
    pod_filters = {
        "namespace": "default",
    }
    metrics_details = mock_metrics_details("GET", "/k8s_pod")
    response = k8s_pod.list_k8s_pods(
        pod_filters=pod_filters, metrics_details=metrics_details
    )
    pods = json.loads(response.body)
    assert len(pods) == 1
    assert pods[0]["namespace"] == "default"

    response = k8s_pod.list_k8s_pods(
        pod_filters={"namespace": "other-namespace"}, metrics_details=metrics_details
    )
    pods = json.loads(response.body)
    assert len(pods) == 0


@patch("app.repositories.k8s.k8s_pod.get_pod_details")
@patch("app.repositories.k8s.k8s_pod.get_k8s_core_v1_client")
def test_list_k8s_pods_filter_by_exclude_namespace_regex(
    mock_get_client, mock_get_pod_details
):
    """Test listing pods excluding namespaces matching a regex."""
    setup_pod_mocks(mock_get_client, mock_get_pod_details)
    pod_filters = {
        "exclude_namespace_regex": "kube-.*",
    }
    metrics_details = mock_metrics_details("GET", "/k8s_pod")
    response = k8s_pod.list_k8s_pods(
        pod_filters=pod_filters, metrics_details=metrics_details
    )
    pods = json.loads(response.body)
    assert len(pods) == 1
    assert pods[0]["namespace"] == "default"


@patch("app.repositories.k8s.k8s_pod.get_pod_details")
@patch("app.repositories.k8s.k8s_pod.get_k8s_core_v1_client")
def test_list_k8s_pods_no_filters_returns_all(mock_get_client, mock_get_pod_details):
    """Test listing pods without any filters returns all pods."""
    setup_pod_mocks(mock_get_client, mock_get_pod_details)
    metrics_details = mock_metrics_details("GET", "/k8s_pod")
    response = k8s_pod.list_k8s_pods(pod_filters={}, metrics_details=metrics_details)
    pods = json.loads(response.body)
    assert len(pods) == 2
    assert {p["name"] for p in pods} == {"test-pod", "other-pod"}


@patch("app.repositories.k8s.k8s_pod.list_k8s_pods")
def test_list_k8s_user_pods_calls_list_k8s_pods(mock_list_k8s_pods):
    """
    Test that list_k8s_user_pods calls list_k8s_pods with the correct parameters.
    """
    pod_filters = {
        "namespace": "default",
        "name": "test",
    }
    metrics_details = mock_metrics_details("GET", "/k8s_user_pod")
    k8s_pod.list_k8s_user_pods(pod_filters=pod_filters, metrics_details=metrics_details)
    mock_list_k8s_pods.assert_called_once()
    _, kwargs = mock_list_k8s_pods.call_args
    assert (
        kwargs["pod_filters"]["exclude_namespace_regex"]
        == k8s_pod.K8S_IN_USE_NAMESPACE_REGEX
    )


@patch("app.repositories.k8s.k8s_pod.get_k8s_core_v1_client")
def test_list_k8s_pods_config_exception(mock_get_client):
    """Test listing pods when Kubernetes configuration raises an exception."""
    mock_get_client.side_effect = ConfigException("configuration error")
    with pytest.raises(K8sConfigException) as exc:
        k8s_pod.list_k8s_pods()
    assert "configuration error" in str(exc.value).lower()


@patch("app.repositories.k8s.k8s_pod.get_k8s_core_v1_client")
def test_list_k8s_pods_value_error(mock_get_client):
    """Test listing pods when a ValueError occurs."""
    mock_get_client.side_effect = ValueError("bad value")
    with pytest.raises(K8sValueError) as exc:
        k8s_pod.list_k8s_pods()
    assert "value error" in str(exc.value).lower()


@patch("app.repositories.k8s.k8s_pod.get_k8s_core_v1_client")
def test_list_k8s_pods_api_exception(mock_get_client):
    """Test listing pods when Kubernetes API raises an exception."""
    mock_get_client.side_effect = ApiException(reason="api fail")
    with pytest.raises(K8sAPIException) as exc:
        k8s_pod.list_k8s_pods()
    assert "api error" in str(exc.value).lower()

@patch("app.repositories.k8s.k8s_pod.get_k8s_core_v1_client")
@patch("app.repositories.k8s.k8s_pod.list_k8s_user_pods")
def test_delete_k8s_user_pod_success(mock_list_user_pods, mock_get_client):
    """Test successful pod deletion."""
    # Simulate finding the pod
    pod_info = {"namespace": "test-ns", "name": "test-pod"}
    mock_response = MagicMock()
    mock_response.body = [pod_info]
    mock_list_user_pods.return_value = mock_response

    mock_core_v1 = MagicMock()
    mock_get_client.return_value = mock_core_v1
    mock_core_v1.delete_namespaced_pod.return_value = None

    response = k8s_pod.delete_k8s_user_pod("test-uid")
    assert response.status_code == 200
    assert json.loads(response.body)["message"] == "Pod deletion triggered successfully"
    mock_core_v1.delete_namespaced_pod.assert_called_once_with(name="test-pod", namespace="test-ns")

@patch("app.repositories.k8s.k8s_pod.list_k8s_user_pods")
def test_delete_k8s_user_pod_not_found(mock_list_user_pods):
    """Test deleting a pod that does not exist or is a system pod returns 404."""
    mock_response = MagicMock()
    mock_response.body = []
    mock_list_user_pods.return_value = mock_response

    response = k8s_pod.delete_k8s_user_pod("nonexistent-uid")
    assert response.status_code == 404
    assert "not found" in json.loads(response.body)["message"]

@patch("app.repositories.k8s.k8s_pod.handle_k8s_exceptions")
@patch("app.repositories.k8s.k8s_pod.get_k8s_core_v1_client")
@patch("app.repositories.k8s.k8s_pod.list_k8s_user_pods")
def test_delete_k8s_pod_api_exception(mock_list_user_pods, mock_get_client, mock_handle):
    """Test pod deletion when Kubernetes API raises an exception."""
    pod_info = {"namespace": "test-ns", "name": "test-pod"}
    mock_response = MagicMock()
    mock_response.body = [pod_info]
    mock_list_user_pods.return_value = mock_response

    mock_core_v1 = MagicMock()
    mock_get_client.return_value = mock_core_v1
    mock_core_v1.delete_namespaced_pod.side_effect = ApiException("api error")

    k8s_pod.delete_k8s_user_pod("test-uid")
    mock_handle.assert_called()
    assert "Kubernetes API error while deleting pod" in mock_handle.call_args[1]["context_msg"]

@patch("app.repositories.k8s.k8s_pod.handle_k8s_exceptions")
@patch("app.repositories.k8s.k8s_pod.get_k8s_core_v1_client")
@patch("app.repositories.k8s.k8s_pod.list_k8s_user_pods")
def test_delete_k8s_pod_config_exception(mock_list_user_pods, mock_get_client, mock_handle):
    """Test pod deletion when Kubernetes config raises an exception."""
    pod_info = {"namespace": "test-ns", "name": "test-pod"}
    mock_response = MagicMock()
    mock_response.body = [pod_info]
    mock_list_user_pods.return_value = mock_response

    mock_core_v1 = MagicMock()
    mock_get_client.return_value = mock_core_v1
    mock_core_v1.delete_namespaced_pod.side_effect = ConfigException("config error")

    k8s_pod.delete_k8s_user_pod("test-uid")
    mock_handle.assert_called()
    assert (
        "Kubernetes configuration error while deleting pod"
        in mock_handle.call_args[1]["context_msg"]
    )

@patch("app.repositories.k8s.k8s_pod.get_k8s_core_v1_client")
@patch("app.repositories.k8s.k8s_pod.list_k8s_user_pods")
def test_delete_k8s_user_pod_body_bytes(mock_list_user_pods, mock_get_client):
    """Test delete_k8s_user_pod when response.body is bytes."""
    pod_info = {"namespace": "test-ns", "name": "test-pod"}
    mock_response = MagicMock()
    mock_response.body = json.dumps([pod_info]).encode("utf-8")
    mock_list_user_pods.return_value = mock_response

    mock_core_v1 = MagicMock()
    mock_get_client.return_value = mock_core_v1

    response = k8s_pod.delete_k8s_user_pod("test-uid")
    assert response.status_code == 200
    assert json.loads(response.body)["message"] == "Pod deletion triggered successfully"
    mock_core_v1.delete_namespaced_pod.assert_called_once_with(name="test-pod", namespace="test-ns")

@patch("app.repositories.k8s.k8s_pod.get_k8s_core_v1_client")
@patch("app.repositories.k8s.k8s_pod.list_k8s_user_pods")
def test_delete_k8s_user_pod_body_str(mock_list_user_pods, mock_get_client):
    """Test delete_k8s_user_pod when response.body is str."""
    pod_info = {"namespace": "test-ns", "name": "test-pod"}
    mock_response = MagicMock()
    mock_response.body = json.dumps([pod_info])
    mock_list_user_pods.return_value = mock_response

    mock_core_v1 = MagicMock()
    mock_get_client.return_value = mock_core_v1

    response = k8s_pod.delete_k8s_user_pod("test-uid")
    assert response.status_code == 200
    assert json.loads(response.body)["message"] == "Pod deletion triggered successfully"
    mock_core_v1.delete_namespaced_pod.assert_called_once_with(name="test-pod", namespace="test-ns")

@patch("app.repositories.k8s.k8s_pod.list_k8s_user_pods")
def test_delete_k8s_user_pod_body_none(mock_list_user_pods):
    """Test delete_k8s_user_pod when response.body is None."""
    mock_response = MagicMock()
    mock_response.body = None
    mock_list_user_pods.return_value = mock_response

    response = k8s_pod.delete_k8s_user_pod("test-uid")
    assert response.status_code == 404
    assert "not found" in json.loads(response.body)["message"]
