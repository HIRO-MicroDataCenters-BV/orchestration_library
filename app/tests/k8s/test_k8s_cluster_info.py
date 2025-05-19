"""
Tests for the k8s_cluster_info module.
"""
from unittest.mock import MagicMock, patch
from kubernetes.client.exceptions import ApiException

from app.repositories.k8s import k8s_cluster_info


# @pytest.fixture
def mock_version_info():
    """
    Mock version information for the Kubernetes cluster.
    """
    version = MagicMock()
    version.git_version = "v1.25.0-test-10.0.0.1"
    version.git_commit = "abcdef123456"
    return version

# @pytest.fixture
def mock_node():
    """
    Mock a Kubernetes node object.
    """
    node = MagicMock()
    node.metadata.name = "node1"
    node.metadata.uid = "uid1"
    node.metadata.annotations = {"anno": "value"}
    node.metadata.labels = {"role": "worker"}
    node.status = MagicMock()  # Explicitly mock node.status
    node.status.conditions = [MagicMock(type="Ready", message="ok", reason="KubeletReady")]
    node.status.node_info = MagicMock()  # Explicitly mock node.status.node_info
    node.status.node_info.architecture = "amd64"
    node.status.node_info.container_runtime_version = "docker://20.10"
    node.status.node_info.kernel_version = "5.10"
    node.status.node_info.kubelet_version = "v1.25.0"
    node.status.node_info.os_image = "Ubuntu"
    node.status.capacity = {"cpu": "4", "memory": "8Gi"}
    node.status.allocatable = {"cpu": "4", "memory": "8Gi"}
    node.spec.taints = []
    node.spec.unschedulable = False
    return node

# @pytest.fixture
def mock_component():
    """
    Mock a Kubernetes component status object.
    """
    comp = MagicMock()
    comp.metadata.name = "scheduler"
    cond = MagicMock(type="Healthy", status="True")
    comp.conditions = [cond]
    return comp

# @pytest.fixture
def mock_pod():
    """
    Mock a Kubernetes pod object in the kube-system namespace.
    """
    pod = MagicMock()
    pod.metadata.name = "kube-proxy"
    pod.metadata.namespace = "kube-system"
    pod.status.phase = "Running"
    pod.spec.node_name = "node1"
    container_status = MagicMock()
    container_status.name = "kube-proxy"
    container_status.ready = True
    container_status.restart_count = 0
    container_status.image = "kube-proxy:v1.25.0"
    pod.status.container_statuses = [container_status]
    return pod

@patch("app.repositories.k8s.k8s_cluster_info.get_k8s_core_v1_client")
@patch("app.repositories.k8s.k8s_cluster_info.get_k8s_version_api_client")
def test_get_cluster_info_success(mock_get_version, mock_get_core):
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

    result = k8s_cluster_info.get_cluster_info()
    assert result["kubernetes_version"] == "v1.25.0-test-10.0.0.1"
    assert result["nodes"][0]["name"] == "node1"
    assert result["components"][0]["name"] == "scheduler"
    assert result["kube_system_pods"][0]["name"] == "kube-proxy"
    assert result["cluster_id"] == "abcdef123456"
    assert result["cluster_name"] == "v1.25.0"
    assert result["cluster_domain"] == "test"
    assert result["cluster_ip"] == "10.0.0.1"

@patch("app.repositories.k8s.k8s_cluster_info.get_k8s_core_v1_client")
@patch("app.repositories.k8s.k8s_cluster_info.get_k8s_version_api_client")
def test_get_cluster_info_handles_exceptions(mock_get_version, mock_get_core):
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

    result = k8s_cluster_info.get_cluster_info()
    assert not result["nodes"]
    assert not result["components"]
    assert not result["kube_system_pods"]
