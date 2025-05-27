"""
Tests for CRUD operations and routes related to K8S Pod management.
"""

from unittest.mock import MagicMock, patch

import json

from app.repositories.k8s import k8s_pod
from app.tests.utils.mock_objects import pod_mock_fixture


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


@patch("app.repositories.k8s.k8s_pod.get_k8s_core_v1_client")
def test_list_k8s_pods_with_filters(mock_get_client):
    """
    Test listing pods with various filters.
    """
    mock_core_v1 = MagicMock()
    mock_core_v1.list_pod_for_all_namespaces.return_value.items = [pod_mock_fixture()]
    mock_get_client.return_value = mock_core_v1

    # Filter by name
    response = k8s_pod.list_k8s_pods(name="test-pod")
    assert response.status_code == 200
    pods = json.loads(response.body)
    assert len(pods) == 1

    # Filter by wrong name
    response = k8s_pod.list_k8s_pods(name="other-pod")
    assert response.status_code == 200
    pods = json.loads(response.body)
    assert len(pods) == 0

    # Filter by wrong pod_id
    response = k8s_pod.list_k8s_pods(pod_id="other-uid")
    assert response.status_code == 200
    pods = json.loads(response.body)
    assert len(pods) == 0

    # Filter by wrong status
    response = k8s_pod.list_k8s_pods(status="Failed")
    assert response.status_code == 200
    pods = json.loads(response.body)
    assert len(pods) == 0

    # Filter by wrong namespace
    response = k8s_pod.list_k8s_pods(namespace="other-namespace")
    assert response.status_code == 200
    pods = json.loads(response.body)
    assert len(pods) == 0

@patch("app.repositories.k8s.k8s_pod.list_k8s_pods")
def test_list_k8s_user_pods_calls_list_k8s_pods(mock_list_k8s_pods):
    """
    Test that list_k8s_user_pods calls list_k8s_pods with the correct parameters.
    """
    k8s_pod.list_k8s_user_pods(namespace="default", name="test")
    mock_list_k8s_pods.assert_called_once()
    _, kwargs = mock_list_k8s_pods.call_args
    assert kwargs["exclude_namespace_regex"] == k8s_pod.K8S_IN_USE_NAMESPACE_REGEX
