"""
Tests for CRUD operations and routes related to K8S Pod management.
"""

from unittest.mock import MagicMock, patch

import json

import pytest
from kubernetes.config.config_exception import ConfigException
from kubernetes.client.rest import ApiException
from app.utils.exceptions import (
    K8sAPIException,
    K8sConfigException,
    K8sValueError
)

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


def setup_pod_mocks(mock_get_client, mock_get_pod_details):
    """ Helper function to set up mock pods for testing.
    """
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
    """ Test listing pods filtered by name.
    """
    setup_pod_mocks(mock_get_client, mock_get_pod_details)
    response = k8s_pod.list_k8s_pods(name="test-pod")
    pods = json.loads(response.body)
    assert len(pods) == 1
    assert pods[0]["name"] == "test-pod"

    response = k8s_pod.list_k8s_pods(name="does-not-exist")
    pods = json.loads(response.body)
    assert len(pods) == 0

@patch("app.repositories.k8s.k8s_pod.get_pod_details")
@patch("app.repositories.k8s.k8s_pod.get_k8s_core_v1_client")
def test_list_k8s_pods_filter_by_pod_id(mock_get_client, mock_get_pod_details):
    """ Test listing pods filtered by pod ID.
    """
    setup_pod_mocks(mock_get_client, mock_get_pod_details)
    response = k8s_pod.list_k8s_pods(pod_id="uid-1")
    pods = json.loads(response.body)
    assert len(pods) == 1
    assert pods[0]["name"] == "test-pod"

    response = k8s_pod.list_k8s_pods(pod_id="no-such-uid")
    pods = json.loads(response.body)
    assert len(pods) == 0

@patch("app.repositories.k8s.k8s_pod.get_pod_details")
@patch("app.repositories.k8s.k8s_pod.get_k8s_core_v1_client")
def test_list_k8s_pods_filter_by_status(mock_get_client, mock_get_pod_details):
    """ Test listing pods filtered by status.
    """
    setup_pod_mocks(mock_get_client, mock_get_pod_details)
    response = k8s_pod.list_k8s_pods(status="Running")
    pods = json.loads(response.body)
    assert len(pods) == 1
    assert pods[0]["name"] == "test-pod"

    response = k8s_pod.list_k8s_pods(status="Pending")
    pods = json.loads(response.body)
    assert len(pods) == 0

@patch("app.repositories.k8s.k8s_pod.get_pod_details")
@patch("app.repositories.k8s.k8s_pod.get_k8s_core_v1_client")
def test_list_k8s_pods_filter_by_namespace(mock_get_client, mock_get_pod_details):
    """ Test listing pods filtered by namespace.
    """
    setup_pod_mocks(mock_get_client, mock_get_pod_details)
    response = k8s_pod.list_k8s_pods(namespace="default")
    pods = json.loads(response.body)
    assert len(pods) == 1
    assert pods[0]["namespace"] == "default"

    response = k8s_pod.list_k8s_pods(namespace="other-namespace")
    pods = json.loads(response.body)
    assert len(pods) == 0

@patch("app.repositories.k8s.k8s_pod.get_pod_details")
@patch("app.repositories.k8s.k8s_pod.get_k8s_core_v1_client")
def test_list_k8s_pods_filter_by_exclude_namespace_regex(mock_get_client, mock_get_pod_details):
    """ Test listing pods excluding namespaces matching a regex.
    """
    setup_pod_mocks(mock_get_client, mock_get_pod_details)
    response = k8s_pod.list_k8s_pods(exclude_namespace_regex="kube-.*")
    pods = json.loads(response.body)
    assert len(pods) == 1
    assert pods[0]["namespace"] == "default"

@patch("app.repositories.k8s.k8s_pod.get_pod_details")
@patch("app.repositories.k8s.k8s_pod.get_k8s_core_v1_client")
def test_list_k8s_pods_no_filters_returns_all(mock_get_client, mock_get_pod_details):
    """ Test listing pods without any filters returns all pods.
    """
    setup_pod_mocks(mock_get_client, mock_get_pod_details)
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
