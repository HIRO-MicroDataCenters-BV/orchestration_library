"""
Tests for the k8s_cluster_info module.
"""

from contextlib import contextmanager
import json
from unittest.mock import MagicMock, patch
from kubernetes.client.exceptions import ApiException
from kubernetes.config.config_exception import ConfigException
import pytest

from app.repositories.k8s import k8s_cluster_info
from app.tests.utils.mock_objects import (
    mock_configmap,
    mock_version_info,
    mock_node,
    mock_component,
    mock_pod,
)
from app.utils.exceptions import K8sAPIException, K8sConfigException


@pytest.mark.parametrize(
    "cpu_str,expected",
    [
        ("1000000n", 1.0),
        ("1000u", 1.0),
        ("250m", 250),
        ("2", 2000),
    ],
)
def test_parse_cpu_and_memory(cpu_str, expected):
    assert k8s_cluster_info.parse_cpu(cpu_str) == expected


@pytest.mark.parametrize(
    "mem_str,expected",
    [
        ("1024Ki", 1.0),
        ("2Mi", 2.0),
        ("1Gi", 1024.0),
        (str(1048576), 1.0),
    ],
)
def test_parse_memory(mem_str, expected):
    assert k8s_cluster_info.parse_memory(mem_str) == expected


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
        mock_core.read_namespaced_config_map.return_value = mock_configmap()
        mock_core.list_component_status.return_value.items = [mock_component()]
        mock_core.list_namespaced_pod.return_value.items = [mock_pod()]
        # Patch read_namespace to return an object with metadata.uid
        mock_namespace_metadata = MagicMock()
        mock_namespace_metadata.uid = "abcdef123456"
        mock_namespace_obj = MagicMock()
        mock_namespace_obj.metadata = mock_namespace_metadata
        mock_core.read_namespace.return_value = mock_namespace_obj
        # mock_core.read_namespace.return_value = SimpleNamespace(
        #     metadata=SimpleNamespace(uid="abcdef123456")
        # )

        # Patch list_namespace to return an object with items as list of objects with metadata.name
        mock_namespace_metadata1 = MagicMock()
        mock_namespace_metadata1.name = "default"
        mock_namespace_item = MagicMock()
        mock_namespace_item.metadata = mock_namespace_metadata1
        mock_core.list_namespace.return_value.items = [mock_namespace_item]
        # mock_core.list_namespace.return_value.items = [
        #     SimpleNamespace(metadata=SimpleNamespace(name="default"))
        # ]

        mocks["mock_core"].return_value = mock_core
        mocks["mock_node_core"].return_value = mock_core

        # Mock apps_v1 and batch_v1 clients
        mock_apps = MagicMock()
        mock_apps.list_namespaced_deployment.return_value.items = []
        mock_apps.list_namespaced_stateful_set.return_value.items = []
        mock_apps.list_namespaced_daemon_set.return_value.items = []
        mocks["mock_apps"].return_value = mock_apps
        # Mock config context
        mocks["mock_config"].load_kube_config.return_value = None
        mocks["mock_config"].load_incluster_config.return_value = None
        mocks["mock_config"].list_kube_config_contexts.return_value = (
            [{"context": {"cluster": "test-cluster"}}],
            {"context": {"cluster": "test-cluster"}},
        )
        mocks["mock_config"].ConfigException = ConfigException
        mocks["mock_config"].list_kube_config_contexts.return_value = (
            [{"context": {"cluster": "test-cluster"}}],
            {"context": {"cluster": "test-cluster"}},
        )

        mock_custom_api = MagicMock()
        mock_custom_api.list_cluster_custom_object.return_value = {"items": []}
        mocks["mock_node_custom"].return_value = mock_custom_api

        response = k8s_cluster_info.get_cluster_info(advanced=True)
        result = json.loads(response.body.decode())
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


def setup_common_mocks(mocks):
    """
    Helper function to set up common mocks for the Kubernetes API clients.
    This function initializes the core client and sets up default return values
    for various API calls to ensure that tests can run without needing a real Kubernetes cluster.
    """
    # Set up all mocks to return valid/empty data by default
    mock_core = MagicMock()
    mock_core.list_namespace.return_value.items = []
    mock_core.list_node.return_value.items = []
    mock_core.list_component_status.return_value.items = []
    mock_core.list_namespaced_pod.return_value.items = []
    mock_core.read_namespace.return_value.metadata.uid = "fake-uid"
    mock_core.read_namespaced_config_map.return_value.data = {
        "ClusterConfiguration": ""
    }
    mocks["mock_core"].return_value = mock_core
    mocks["mock_node_core"].return_value = mock_core
    mocks["mock_apps"].return_value = MagicMock()
    mocks["mock_batch"].return_value = MagicMock()
    mocks["mock_config"].list_kube_config_contexts.return_value = (
        [],
        {"context": {"cluster": None}},
    )
    return mock_core


def test_get_cluster_info_namespace_exception():
    """Test the get_cluster_info function when listing namespaces fails.
    This test checks if the function raises a K8sAPIException when the namespace list
    cannot be retrieved due to an API error.
    """
    with patch("kubernetes.config.load_kube_config", return_value=None), patch(
        "kubernetes.config.load_incluster_config", return_value=None
    ), k8s_cluster_info_mocks() as mocks:
        mock_core = setup_common_mocks(mocks)
        mock_core.list_namespace.side_effect = ApiException("namespace list error")
        with pytest.raises(K8sAPIException) as excinfo:
            k8s_cluster_info.get_cluster_info(advanced=True)
        assert "namespace list error" in str(excinfo.value)


def test_get_cluster_info_nodes_exception():
    """Test the get_cluster_info function when listing nodes fails.
    This test checks if the function raises a K8sAPIException when the node list
    cannot be retrieved due to an API error.
    """
    with patch("kubernetes.config.load_kube_config", return_value=None), patch(
        "kubernetes.config.load_incluster_config", return_value=None
    ), k8s_cluster_info_mocks() as mocks:
        mock_core = setup_common_mocks(mocks)
        mock_core.list_node.side_effect = ApiException("nodes error")
        # Remove side effect for list_namespace so nodes is reached
        mock_core.list_namespace.side_effect = None
        with pytest.raises(K8sAPIException) as excinfo:
            k8s_cluster_info.get_cluster_info(advanced=True)
        assert "nodes error" in str(excinfo.value)


def test_get_cluster_info_config_exception():
    """
    Test the get_cluster_info function when the Kubernetes configuration loading fails.
    This test checks if the function raises a K8sConfigException when the configuration
    cannot be loaded.
    """
    with patch("kubernetes.config.load_kube_config", return_value=None), patch(
        "kubernetes.config.load_incluster_config", return_value=None
    ), k8s_cluster_info_mocks() as mocks:
        mock_core = setup_common_mocks(mocks)
        # Remove side effect for list_namespace so config is reached
        mock_core.list_namespace.side_effect = None
        # Patch config.load_incluster_config to raise ConfigException
        mocks["mock_config"].load_incluster_config.side_effect = ConfigException(
            "config error"
        )
        with pytest.raises(K8sConfigException) as excinfo:
            k8s_cluster_info.get_cluster_info(advanced=True)
        assert "config error" in str(excinfo.value)
