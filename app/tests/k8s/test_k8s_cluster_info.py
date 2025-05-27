"""
Tests for the k8s_cluster_info module.
"""
from unittest.mock import MagicMock, patch
from kubernetes.client.exceptions import ApiException

from app.repositories.k8s import k8s_cluster_info
from app.tests.utils.mock_objects import (mock_version_info,
                                          mock_node,
                                          mock_component,
                                          mock_pod,
                                          mock_custom_api)


@patch("app.repositories.k8s.k8s_node.get_k8s_core_v1_client")
@patch("app.repositories.k8s.k8s_node.get_k8s_custom_objects_client")
@patch("app.repositories.k8s.k8s_cluster_info.get_k8s_core_v1_client")
@patch("app.repositories.k8s.k8s_cluster_info.get_k8s_version_api_client")
def test_get_cluster_info_success(mock_get_version,
                                  mock_get_core,
                                  mock_get_custom,
                                  mock_get_k8s_core):
    """
    Test the successful retrieval of cluster information.
    """
    # Mock version API
    mock_get_version.return_value.get_code.return_value = mock_version_info()

    # Mock core_v1 client
    mock_core = MagicMock()
    mock_core.list_node.return_value.items = [mock_node()]
    mock_core.list_component_status.return_value.items = [mock_component()]
    mock_core.list_namespaced_pod.return_value.items = [mock_pod()]
    mock_get_core.return_value = mock_core
    mock_get_k8s_core.return_value = mock_core

    mock_get_custom.return_value = mock_custom_api()

    result = k8s_cluster_info.get_cluster_info()
    assert result["kubernetes_version"] == "v1.25.0-test-10.0.0.1"
    assert result["nodes"][0]["name"] == "test-node"
    assert result["components"][0]["name"] == "scheduler"
    assert result["kube_system_pods"][0]["name"] == "kube-proxy"
    assert result["cluster_id"] == "abcdef123456"


@patch("app.repositories.k8s.k8s_node.get_k8s_core_v1_client")
@patch("app.repositories.k8s.k8s_node.get_k8s_custom_objects_client")
@patch("app.repositories.k8s.k8s_cluster_info.get_k8s_core_v1_client")
@patch("app.repositories.k8s.k8s_cluster_info.get_k8s_version_api_client")
def test_get_cluster_info_handles_exceptions(mock_get_version,
                                             mock_get_core,
                                             mock_get_custom,
                                             mock_get_k8s_core):
    """
    Test the handling of exceptions when retrieving cluster information.
    """
    # Mock version API
    mock_get_version.return_value.get_code.return_value = mock_version_info()

    # Mock core_v1 client to raise exceptions
    mock_core = MagicMock()

    mock_core.list_node.side_effect = ApiException("nodes error")
    mock_core.list_component_status.side_effect = ApiException("components error")
    mock_core.list_namespaced_pod.side_effect = ApiException("pods error")
    mock_get_core.return_value = mock_core
    mock_get_k8s_core.return_value = mock_core

    mock_get_custom.return_value = mock_custom_api()

    result = k8s_cluster_info.get_cluster_info()
    assert not result["nodes"]
    assert not result["components"]
    assert not result["kube_system_pods"]
