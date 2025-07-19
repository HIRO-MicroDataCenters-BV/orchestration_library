"""
Tests for CRUD operations and routes related to K8S Pod management.
"""

from unittest.mock import MagicMock, patch

import json

import pytest

from app.repositories.k8s import k8s_pod
from app.tests.utils.mock_objects import pod_mock_fixture
from kubernetes.config.config_exception import ConfigException
from app.utils.exceptions import K8sAPIException, K8sConfigException, K8sValueError
from kubernetes.client.rest import ApiException


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

    response = k8s_pod.list_k8s_pods(namespace="default")
    assert response.status_code == 200
    pods = json.loads(response.body)
    assert pods[0]["namespace"] == "default"


@patch("app.repositories.k8s.k8s_pod.get_pod_details")
@patch("app.repositories.k8s.k8s_pod.get_k8s_core_v1_client")
def test_list_k8s_pods_with_filters(mock_get_client, mock_get_pod_details):
    """
    Test listing pods with various filters, including exclude_namespace_regex.
    """
    # Create two pod mocks with different names, uids, namespaces, and statuses
    pod1 = MagicMock()
    pod1.metadata.name = "test-pod"
    pod1.metadata.uid = "uid-1"
    pod1.metadata.namespace = "default"
    pod1.status.phase = "Running"

    pod2 = MagicMock()
    pod2.metadata.name = "other-pod"
    pod2.metadata.uid = "uid-2"
    pod2.metadata.namespace = "kube-system"
    pod2.status.phase = "Failed"

    # Simulate both pods returned
    mock_core_v1 = MagicMock()
    mock_core_v1.list_pod_for_all_namespaces.return_value.items = [pod1, pod2]
    mock_core_v1.list_namespaced_pod.return_value.items = [pod1]
    mock_get_client.return_value = mock_core_v1

    # get_pod_details returns a dict with the pod name
    mock_get_pod_details.side_effect = lambda pod: {
        "name": pod.metadata.name,
        "namespace": pod.metadata.namespace,
    }

    # Filter by name (should match pod1 only)
    response = k8s_pod.list_k8s_pods(name="test-pod")
    pods = json.loads(response.body)
    assert len(pods) == 1
    assert pods[0]["name"] == "test-pod"

    # Filter by wrong name (should match none)
    response = k8s_pod.list_k8s_pods(name="does-not-exist")
    pods = json.loads(response.body)
    assert len(pods) == 0

    # Filter by pod_id (should match pod1 only)
    response = k8s_pod.list_k8s_pods(pod_id="uid-1")
    pods = json.loads(response.body)
    assert len(pods) == 1
    assert pods[0]["name"] == "test-pod"

    # Filter by wrong pod_id (should match none)
    response = k8s_pod.list_k8s_pods(pod_id="no-such-uid")
    pods = json.loads(response.body)
    assert len(pods) == 0

    # Filter by status (should match pod1 only)
    response = k8s_pod.list_k8s_pods(status="Running")
    pods = json.loads(response.body)
    assert len(pods) == 1
    assert pods[0]["name"] == "test-pod"

    # Filter by wrong status (should match none)
    response = k8s_pod.list_k8s_pods(status="Pending")
    pods = json.loads(response.body)
    assert len(pods) == 0

    # Filter by namespace (should use list_namespaced_pod and match pod1)
    response = k8s_pod.list_k8s_pods(namespace="default")
    pods = json.loads(response.body)
    assert len(pods) == 1
    assert pods[0]["namespace"] == "default"

    # Filter by namespace that does not match any pod (should match none)
    response = k8s_pod.list_k8s_pods(namespace="other-namespace")
    pods = json.loads(response.body)
    assert len(pods) == 0

    # Filter by exclude_namespace_regex (should exclude pod2)
    response = k8s_pod.list_k8s_pods(exclude_namespace_regex="kube-.*")
    pods = json.loads(response.body)
    assert len(pods) == 1
    assert pods[0]["namespace"] == "default"

    # Both pods would be included if no filters
    response = k8s_pod.list_k8s_pods()
    pods = json.loads(response.body)
    assert len(pods) == 2
    assert {p["name"] for p in pods} == {"test-pod", "other-pod"}


@patch("app.repositories.k8s.k8s_pod.list_k8s_pods")
def test_list_k8s_user_pods_calls_list_k8s_pods(mock_list_k8s_pods):
    """
    Test that list_k8s_user_pods calls list_k8s_pods with the correct parameters.
    """
    k8s_pod.list_k8s_user_pods(namespace="default", name="test")
    mock_list_k8s_pods.assert_called_once()
    _, kwargs = mock_list_k8s_pods.call_args
    assert kwargs["exclude_namespace_regex"] == k8s_pod.K8S_IN_USE_NAMESPACE_REGEX


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
