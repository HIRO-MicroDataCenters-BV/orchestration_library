"""
Tests for the k8s_cluster_info module.
"""
from unittest.mock import MagicMock, patch
from kubernetes.client.exceptions import ApiException
from kubernetes.config.config_exception import ConfigException

from app.repositories.k8s import k8s_cluster_info
from app.tests.utils.mock_objects import (
    mock_version_info,
    mock_node,
    mock_component,
    mock_pod,
    mock_custom_api,
)

@patch("app.repositories.k8s.k8s_node.get_k8s_core_v1_client", autospec=True)
@patch("app.repositories.k8s.k8s_node.get_k8s_custom_objects_client", autospec=True)
@patch("app.repositories.k8s.k8s_cluster_info.get_k8s_core_v1_client", autospec=True)
@patch("app.repositories.k8s.k8s_cluster_info.get_k8s_version_api_client", autospec=True)
@patch("app.repositories.k8s.k8s_cluster_info.get_k8s_apps_v1_client", autospec=True)
@patch("app.repositories.k8s.k8s_cluster_info.get_k8s_batch_v1_client", autospec=True)
@patch("app.repositories.k8s.k8s_cluster_info.config", autospec=True)
def test_get_cluster_info_success(
    mock_config,
    mock_get_batch,
    mock_get_apps,
    mock_get_version,
    mock_get_core,
    mock_get_custom,
    mock_get_k8s_core,
):
    # Mock version API
    mock_get_version.return_value.get_code.return_value = mock_version_info()

    # Mock core_v1 client
    mock_core = MagicMock()
    mock_core.list_node.return_value.items = [mock_node()]
    mock_core.list_component_status.return_value.items = [mock_component()]
    mock_core.list_namespaced_pod.return_value.items = [mock_pod()]
    mock_core.read_namespace.return_value.metadata.uid = "abcdef123456"
    mock_namespace = MagicMock()
    mock_namespace.metadata.name = "default"
    mock_core.list_namespace.return_value.items = [mock_namespace]
    mock_get_core.return_value = mock_core
    mock_get_k8s_core.return_value = mock_core

    # Mock apps_v1 and batch_v1 clients
    mock_apps = MagicMock()
    mock_apps.list_namespaced_deployment.return_value.items = []
    mock_apps.list_namespaced_stateful_set.return_value.items = []
    mock_apps.list_namespaced_daemon_set.return_value.items = []
    mock_get_apps.return_value = mock_apps

    mock_batch = MagicMock()
    mock_batch.list_namespaced_job.return_value.items = []
    mock_get_batch.return_value = mock_batch

    # Mock config context
    mock_config.load_incluster_config.return_value = None
    mock_config.list_kube_config_contexts.return_value = (
        [{"context": {"cluster": "test-cluster"}}],
        {"context": {"cluster": "test-cluster"}},
    )

    result = k8s_cluster_info.get_cluster_info()
    assert result["kubernetes_version"] == "v1.25.0-test-10.0.0.1"
    assert result["nodes"][0]["name"] == "test-node"
    assert result["components"][0]["name"] == "scheduler"
    assert result["kube_system_pods"][0]["name"] == "kube-proxy"
    assert result["cluster_id"] == "abcdef123456"
    assert result["cluster_name"] == "test-cluster"
    assert result["namespaces"] == ["default"]
    assert len(result["pods"]) == 1
    assert result["pods"][0]["name"] == "kube-proxy"
    assert result["deployments"] == []
    assert result["jobs"] == []
    assert result["statefulsets"] == []
    assert result["daemonsets"] == []

@patch("app.repositories.k8s.k8s_node.get_k8s_core_v1_client", autospec=True)
@patch("app.repositories.k8s.k8s_node.get_k8s_custom_objects_client", autospec=True)
@patch("app.repositories.k8s.k8s_cluster_info.get_k8s_core_v1_client", autospec=True)
@patch("app.repositories.k8s.k8s_cluster_info.get_k8s_version_api_client", autospec=True)
@patch("app.repositories.k8s.k8s_cluster_info.get_k8s_apps_v1_client", autospec=True)
@patch("app.repositories.k8s.k8s_cluster_info.get_k8s_batch_v1_client", autospec=True)
@patch("app.repositories.k8s.k8s_cluster_info.config", autospec=True)
def test_get_cluster_info_handles_exceptions(
    mock_config,
    mock_get_batch,
    mock_get_apps,
    mock_get_version,
    mock_get_core,
    mock_get_custom,
    mock_get_k8s_core,
):
    mock_get_version.return_value.get_code.return_value = mock_version_info()
    mock_core = MagicMock()
    mock_core.list_node.side_effect = ApiException("nodes error")
    mock_core.list_component_status.side_effect = ApiException("components error")
    mock_core.list_namespaced_pod.side_effect = ApiException("pods error")
    mock_core.read_namespace.side_effect = ApiException("namespace error")
    mock_core.list_namespace.side_effect = ApiException("namespace list error")
    mock_get_core.return_value = mock_core
    mock_get_k8s_core.return_value = mock_core

    mock_get_apps.return_value = MagicMock()
    mock_get_batch.return_value = MagicMock()
    mock_config.load_incluster_config.side_effect = ConfigException("config error")
    mock_config.list_kube_config_contexts.side_effect = ConfigException("context error")
    mock_config.ConfigException = ConfigException

    result = k8s_cluster_info.get_cluster_info()
    assert result["nodes"] == []
    assert result["components"] == []
    assert result["kube_system_pods"] == []
    assert result["cluster_id"] is None
    assert result["cluster_name"] is None
    assert result["namespaces"] == []