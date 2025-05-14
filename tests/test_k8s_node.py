"""
Tests for node get and list functionality in Kubernetes.
"""
import json
from unittest.mock import MagicMock, patch

from app.crud import k8s_node


def mock_node():
    """
    Mock a Kubernetes node object with various attributes.
    """
    node = MagicMock()
    node.api_version = "v1"
    node.metadata.uid = "node-uid"
    node.metadata.name = "test-node"
    node.metadata.labels = {"role": "worker"}
    node.metadata.annotations = {"anno": "value"}
    # Node conditions
    condition = MagicMock()
    condition.type = "Ready"
    condition.message = "Node is ready"
    condition.reason = "KubeletReady"
    node.status.conditions = [condition]
    # Node info
    node_info = MagicMock()
    node_info.architecture = "amd64"
    node_info.container_runtime_version = "docker://20.10"
    node_info.kernel_version = "5.10"
    node_info.kubelet_version = "v1.21.0"
    node_info.os_image = "Ubuntu 20.04"
    node.status.node_info = node_info
    # Capacity and allocatable
    node.status.capacity = {"cpu": "4", "memory": "8Gi"}
    node.status.allocatable = {"cpu": "4", "memory": "8Gi"}
    # Addresses
    address = MagicMock()
    address.type = "InternalIP"
    address.address = "192.168.1.10"
    node.status.addresses = [address]
    # Pod CIDR
    node.spec.pod_cidr = "10.244.0.0/24"
    # Taints
    taint = MagicMock()
    taint.key = "node-role.kubernetes.io/master"
    taint.value = "true"
    taint.effect = "NoSchedule"
    node.spec.taints = [taint]
    node.spec.unschedulable = False
    return node

@patch("app.crud.k8s_node.get_k8s_core_v1_client")
def test_list_k8s_nodes_all(mock_get_client):
    """
    Test listing all nodes in the cluster.
    """
    mock_core_v1 = MagicMock()
    mock_core_v1.list_node.return_value.items = [mock_node()]
    mock_get_client.return_value = mock_core_v1

    response = k8s_node.list_k8s_nodes()
    assert response.status_code == 200

    nodes = json.loads(response.body)
    assert len(nodes) == 1
    assert nodes[0]["name"] == "test-node"
    assert nodes[0]["status"] == "Ready"
    assert nodes[0]["node_info"]["architecture"] == "amd64"
    assert nodes[0]["capacity"]["cpu"] == "4"
    assert nodes[0]["addresses"][0]["address"] == "192.168.1.10"

@patch("app.crud.k8s_node.get_k8s_core_v1_client")
def test_list_k8s_nodes_with_filters(mock_get_client):
    """
    Test listing nodes with various filters.
    """
    mock_core_v1 = MagicMock()
    mock_core_v1.list_node.return_value.items = [mock_node()]
    mock_get_client.return_value = mock_core_v1

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
