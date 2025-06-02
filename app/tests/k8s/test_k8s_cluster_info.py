"""
Tests for the k8s_cluster_info module.
"""

from contextlib import contextmanager
from unittest.mock import MagicMock, patch
from kubernetes.client.exceptions import ApiException
from kubernetes.config.config_exception import ConfigException

from app.repositories.k8s import k8s_cluster_info
from app.tests.utils.mock_objects import (
    mock_version_info,
    mock_node,
    mock_component,
    mock_pod,
)


@contextmanager
def k8s_cluster_info_mocks():
    """
    Fixture to mock Kubernetes API clients and configuration.
    This fixture provides mocked clients for core, apps, batch, and version APIs,
    as well as the configuration loading functions.
    It allows tests to simulate various scenarios without needing a real Kubernetes cluster.
    """
    with patch(
        "app.repositories.k8s.k8s_node.get_k8s_core_v1_client"
    ) as mock_node_core, patch(
        "app.repositories.k8s.k8s_node.get_k8s_custom_objects_client"
    ) as mock_node_custom, patch(
        "app.repositories.k8s.k8s_cluster_info.get_k8s_core_v1_client"
    ) as mock_core, patch(
        "app.repositories.k8s.k8s_cluster_info.get_k8s_version_api_client"
    ) as mock_version, patch(
        "app.repositories.k8s.k8s_cluster_info.get_k8s_apps_v1_client"
    ) as mock_apps, patch(
        "app.repositories.k8s.k8s_cluster_info.get_k8s_batch_v1_client"
    ) as mock_batch, patch(
        "app.repositories.k8s.k8s_cluster_info.config"
    ) as mock_config:
        yield {
            "mock_node_core": mock_node_core,
            "mock_node_custom": mock_node_custom,
            "mock_core": mock_core,
            "mock_version": mock_version,
            "mock_apps": mock_apps,
            "mock_batch": mock_batch,
            "mock_config": mock_config,
        }


def test_get_cluster_info_success():
    """
    Test the get_cluster_info function with mocked Kubernetes API responses.
    This test checks if the function correctly aggregates information about nodes,
    components, pods, and other resources in the cluster.
    """
    with patch("kubernetes.config.load_kube_config", return_value=None), patch(
        "kubernetes.config.load_incluster_config", return_value=None
    ), k8s_cluster_info_mocks() as mocks:
        # Mock version API
        mocks["mock_version"].return_value.get_code.return_value = mock_version_info()

        # Mock core_v1 client
        mock_core = MagicMock()
        mock_core.list_node.return_value.items = [mock_node()]
        mock_core.list_component_status.return_value.items = [mock_component()]
        mock_core.list_namespaced_pod.return_value.items = [mock_pod()]
        mock_core.read_namespace.return_value.metadata.uid = "abcdef123456"
        mock_namespace = MagicMock()
        mock_namespace.metadata.name = "default"
        mock_core.list_namespace.return_value.items = [mock_namespace]
        mocks["mock_core"].return_value = mock_core
        mocks["mock_node_core"].return_value = mock_core

        # Mock apps_v1 and batch_v1 clients
        mock_apps = MagicMock()
        mock_apps.list_namespaced_deployment.return_value.items = []
        mock_apps.list_namespaced_stateful_set.return_value.items = []
        mock_apps.list_namespaced_daemon_set.return_value.items = []
        mocks["mock_apps"].return_value = mock_apps

        mock_batch = MagicMock()
        mock_batch.list_namespaced_job.return_value.items = []
        mocks["mock_batch"].return_value = mock_batch

        # Mock config context
        mocks["mock_config"].load_kube_config.return_value = MagicMock()
        mocks["mock_config"].load_incluster_config.return_value = MagicMock()
        mocks["mock_config"].list_kube_config_contexts.return_value = (
            [{"context": {"cluster": "test-cluster"}}],
            {"context": {"cluster": "test-cluster"}},
        )

        mock_custom_api = MagicMock()
        mock_custom_api.list_cluster_custom_object.return_value = {"items": []}
        mocks["mock_node_custom"].return_value = mock_custom_api

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


def test_get_cluster_info_handles_exceptions():
    """
    Test the get_cluster_info function when various Kubernetes API calls raise exceptions.
    This test checks if the function gracefully handles errors and returns empty lists
    or None where appropriate.
    """
    with patch("kubernetes.config.load_kube_config", return_value=None), patch(
        "kubernetes.config.load_incluster_config", return_value=None
    ), k8s_cluster_info_mocks() as mocks:
        mocks["mock_version"].return_value.get_code.return_value = mock_version_info()
        mock_core = MagicMock()
        mock_core.list_node.side_effect = ApiException("nodes error")
        mock_core.list_component_status.side_effect = ApiException("components error")
        mock_core.list_namespaced_pod.side_effect = ApiException("pods error")
        mock_core.read_namespace.side_effect = ApiException("namespace error")
        mock_core.list_namespace.side_effect = ApiException("namespace list error")
        mocks["mock_core"].return_value = mock_core
        mocks["mock_node_core"].return_value = mock_core

        mocks["mock_apps"].return_value = MagicMock()
        mocks["mock_batch"].return_value = MagicMock()
        mocks["mock_config"].load_incluster_config.side_effect = ConfigException(
            "config error"
        )
        mocks["mock_config"].list_kube_config_contexts.side_effect = ConfigException(
            "context error"
        )
        mocks["mock_config"].ConfigException = ConfigException
        mocks["mock_config"].load_kube_config.return_value = None

        result = k8s_cluster_info.get_cluster_info()
        assert not result["nodes"]
        assert not result["components"]
        assert not result["kube_system_pods"]
        assert result["cluster_id"] is None
        assert result["cluster_name"] is None
        assert not result["namespaces"]
