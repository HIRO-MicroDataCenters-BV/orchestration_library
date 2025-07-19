"""
Tests for node get and list functionality in Kubernetes.
"""
import json
from unittest.mock import MagicMock, patch
from kubernetes.client.exceptions import ApiException
from kubernetes.config.config_exception import ConfigException
import pytest

from app.repositories.k8s import k8s_node
from app.tests.utils.mock_objects import mock_node, mock_custom_api
from app.utils.exceptions import K8sAPIException, K8sConfigException, K8sValueError


@patch("app.repositories.k8s.k8s_node.get_k8s_custom_objects_client")
@patch("app.repositories.k8s.k8s_node.get_k8s_core_v1_client")
def test_list_k8s_nodes_all(mock_get_client, mock_get_custom):
    """
    Test listing all nodes in the cluster.
    """
    mock_core_v1 = MagicMock()
    mock_core_v1.list_node.return_value.items = [mock_node()]
    mock_get_client.return_value = mock_core_v1

    mock_get_custom.return_value = mock_custom_api()

    response = k8s_node.list_k8s_nodes()
    assert response.status_code == 200

    nodes = json.loads(response.body)
    assert len(nodes) == 1
    assert nodes[0]["name"] == "test-node"
    assert nodes[0]["status"] == "Ready"
    assert nodes[0]["node_info"]["architecture"] == "amd64"
    assert nodes[0]["capacity"]["cpu"] == "4"
    assert nodes[0]["usage"]["cpu"] == "100m"
    assert nodes[0]["addresses"][0]["address"] == "192.168.1.10"

@patch("app.repositories.k8s.k8s_node.get_k8s_custom_objects_client")
@patch("app.repositories.k8s.k8s_node.get_k8s_core_v1_client")
def test_list_k8s_nodes_with_filters(mock_get_client, mock_get_custom):
    """
    Test listing nodes with various filters.
    """
    mock_core_v1 = MagicMock()
    mock_core_v1.list_node.return_value.items = [mock_node()]
    mock_get_client.return_value = mock_core_v1

    mock_get_custom.return_value = mock_custom_api()

    # Filter by name (should match)
    response = k8s_node.list_k8s_nodes(name="test-node")
    nodes = json.loads(response.body)
    assert len(nodes) == 1
    assert nodes[0]["name"] == "test-node"

    # Filter by wrong name (should not match)
    response = k8s_node.list_k8s_nodes(name="other-node")
    nodes = json.loads(response.body)
    assert len(nodes) == 0

    # Filter by node_id (should match)
    response = k8s_node.list_k8s_nodes(node_id="node-uid")
    nodes = json.loads(response.body)
    assert len(nodes) == 1
    assert nodes[0]["id"] == "node-uid"

    # Filter by wrong node_id (should not match)
    response = k8s_node.list_k8s_nodes(node_id="other-uid")
    nodes = json.loads(response.body)
    assert len(nodes) == 0

    # Filter by status (should match)
    response = k8s_node.list_k8s_nodes(status="Ready")
    nodes = json.loads(response.body)
    assert len(nodes) == 1
    assert nodes[0]["status"] == "Ready"

    # Filter by wrong status (should not match)
    response = k8s_node.list_k8s_nodes(status="NotReady")
    nodes = json.loads(response.body)
    assert len(nodes) == 0

@patch("app.repositories.k8s.k8s_node.get_k8s_core_v1_client")
@patch("app.repositories.k8s.k8s_node.get_k8s_custom_objects_client")
def test_list_k8s_nodes_metrics_api_exception(mock_get_custom, mock_get_core):
    """
    Test listing nodes when metrics.k8s.io API raises an exception.
    """
    mock_core_v1 = MagicMock()
    mock_core_v1.list_node.return_value.items = [mock_node()]
    mock_get_core.return_value = mock_core_v1

    # Simulate metrics.k8s.io API exception
    mock_custom_api1 = MagicMock()
    mock_custom_api1.list_cluster_custom_object.side_effect = ApiException("metrics error")
    mock_get_custom.return_value = mock_custom_api1

    response = k8s_node.list_k8s_nodes()
    assert response.status_code == 200
    nodes = json.loads(response.body)
    assert len(nodes) == 1
    assert nodes[0]["usage"] == {}

@patch("app.repositories.k8s.k8s_node.get_k8s_core_v1_client")
@patch("app.repositories.k8s.k8s_node.get_k8s_custom_objects_client")
def test_list_k8s_nodes_api_exception(mock_get_custom, mock_get_core):
    """Test APIException handling in list_k8s_nodes."""
    mock_get_core.side_effect = ApiException("api error")
    with pytest.raises(K8sAPIException):
        k8s_node.list_k8s_nodes()

@patch("app.repositories.k8s.k8s_node.get_k8s_core_v1_client")
@patch("app.repositories.k8s.k8s_node.get_k8s_custom_objects_client")
def test_list_k8s_nodes_config_exception(mock_get_custom, mock_get_core):
    """Test ConfigException handling in list_k8s_nodes."""
    mock_get_core.side_effect = ConfigException("config error")
    with pytest.raises(K8sConfigException):
        k8s_node.list_k8s_nodes()

@patch("app.repositories.k8s.k8s_node.get_k8s_core_v1_client")
@patch("app.repositories.k8s.k8s_node.get_k8s_custom_objects_client")
def test_list_k8s_nodes_value_error(mock_get_custom, mock_get_core):
    """Test ValueError handling in list_k8s_nodes."""
    mock_get_core.side_effect = ValueError("bad value")
    with pytest.raises(K8sValueError):
        k8s_node.list_k8s_nodes()