"""
Tests for common pod functionality in Kubernetes.
"""

from unittest.mock import MagicMock
from app.repositories.k8s import k8s_common


def test_get_k8s_core_v1_client_incluster(monkeypatch):
    """Test get_k8s_core_v1_client with in-cluster config."""
    load_incluster = MagicMock()
    load_kube = MagicMock()
    core_v1_api = MagicMock()

    monkeypatch.setattr(k8s_common.config, "load_incluster_config", load_incluster)
    monkeypatch.setattr(k8s_common.config, "load_kube_config", load_kube)
    monkeypatch.setattr(k8s_common.kubernetes.client, "CoreV1Api", lambda: core_v1_api)

    # Simulate in-cluster config works (no exception)
    client = k8s_common.get_k8s_core_v1_client()
    load_incluster.assert_called_once()
    load_kube.assert_not_called()
    assert client == core_v1_api


def test_get_k8s_core_v1_client_kubeconfig(monkeypatch):
    """Test get_k8s_core_v1_client falls back to kubeconfig."""

    def raise_config_exception():
        raise k8s_common.config.ConfigException

    load_incluster = MagicMock(side_effect=raise_config_exception)
    load_kube = MagicMock()
    core_v1_api = MagicMock()

    monkeypatch.setattr(k8s_common.config, "load_incluster_config", load_incluster)
    monkeypatch.setattr(k8s_common.config, "load_kube_config", load_kube)
    monkeypatch.setattr(k8s_common.kubernetes.client, "CoreV1Api", lambda: core_v1_api)

    client = k8s_common.get_k8s_core_v1_client()
    load_incluster.assert_called_once()
    load_kube.assert_called_once()
    assert client == core_v1_api


def test_get_k8s_custom_objects_client_incluster(monkeypatch):
    """Test get_k8s_custom_objects_client with in-cluster config."""
    load_incluster = MagicMock()
    load_kube = MagicMock()
    custom_objects_api = MagicMock()

    monkeypatch.setattr(k8s_common.config, "load_incluster_config", load_incluster)
    monkeypatch.setattr(k8s_common.config, "load_kube_config", load_kube)
    monkeypatch.setattr(
        k8s_common.kubernetes.client, "CustomObjectsApi", lambda: custom_objects_api
    )

    # Simulate in-cluster config works (no exception)
    client = k8s_common.get_k8s_custom_objects_client()
    load_incluster.assert_called_once()
    load_kube.assert_not_called()
    assert client == custom_objects_api


def test_get_k8s_custom_objects_client_kubeconfig(monkeypatch):
    """Test get_k8s_custom_objects_client falls back to kubeconfig."""

    def raise_config_exception():
        raise k8s_common.config.ConfigException

    load_incluster = MagicMock(side_effect=raise_config_exception)
    load_kube = MagicMock()
    custom_objects_api = MagicMock()

    monkeypatch.setattr(k8s_common.config, "load_incluster_config", load_incluster)
    monkeypatch.setattr(k8s_common.config, "load_kube_config", load_kube)
    monkeypatch.setattr(
        k8s_common.kubernetes.client, "CustomObjectsApi", lambda: custom_objects_api
    )

    client = k8s_common.get_k8s_custom_objects_client()
    load_incluster.assert_called_once()
    load_kube.assert_called_once()
    assert client == custom_objects_api

def test_get_k8s_version_api_client_incluster(monkeypatch):
    """Test get_k8s_version_api_client with in-cluster config."""
    load_incluster = MagicMock()
    load_kube = MagicMock()
    version_api = MagicMock()

    monkeypatch.setattr(k8s_common.config, "load_incluster_config", load_incluster)
    monkeypatch.setattr(k8s_common.config, "load_kube_config", load_kube)
    monkeypatch.setattr(
        k8s_common.kubernetes.client, "VersionApi", lambda: version_api
    )

    # Simulate in-cluster config works (no exception)
    client = k8s_common.get_k8s_version_api_client()
    load_incluster.assert_called_once()
    load_kube.assert_not_called()
    assert client == version_api

def test_get_k8s_version_api_client_kubeconfig(monkeypatch):
    """Test get_k8s_version_api_client falls back to kubeconfig."""

    def raise_config_exception():
        raise k8s_common.config.ConfigException

    load_incluster = MagicMock(side_effect=raise_config_exception)
    load_kube = MagicMock()
    version_api = MagicMock()

    monkeypatch.setattr(k8s_common.config, "load_incluster_config", load_incluster)
    monkeypatch.setattr(k8s_common.config, "load_kube_config", load_kube)
    monkeypatch.setattr(
        k8s_common.kubernetes.client, "VersionApi", lambda: version_api
    )

    client = k8s_common.get_k8s_version_api_client()
    load_incluster.assert_called_once()
    load_kube.assert_called_once()
    assert client == version_api

def test_get_k8s_apps_v1_client_incluster(monkeypatch):
    """Test get_k8s_apps_v1_client with in-cluster config."""
    load_incluster = MagicMock()
    load_kube = MagicMock()
    apps_v1_api = MagicMock()

    monkeypatch.setattr(k8s_common.config, "load_incluster_config", load_incluster)
    monkeypatch.setattr(k8s_common.config, "load_kube_config", load_kube)
    monkeypatch.setattr(
        k8s_common.kubernetes.client, "AppsV1Api", lambda: apps_v1_api
    )

    # Simulate in-cluster config works (no exception)
    client = k8s_common.get_k8s_apps_v1_client()
    load_incluster.assert_called_once()
    load_kube.assert_not_called()
    assert client == apps_v1_api

def test_get_k8s_apps_v1_client_kubeconfig(monkeypatch):
    """Test get_k8s_apps_v1_client falls back to kubeconfig."""

    def raise_config_exception():
        raise k8s_common.config.ConfigException

    load_incluster = MagicMock(side_effect=raise_config_exception)
    load_kube = MagicMock()
    apps_v1_api = MagicMock()

    monkeypatch.setattr(k8s_common.config, "load_incluster_config", load_incluster)
    monkeypatch.setattr(k8s_common.config, "load_kube_config", load_kube)
    monkeypatch.setattr(
        k8s_common.kubernetes.client, "AppsV1Api", lambda: apps_v1_api
    )

    client = k8s_common.get_k8s_apps_v1_client()
    load_incluster.assert_called_once()
    load_kube.assert_called_once()
    assert client == apps_v1_api

def test_get_k8s_batch_v1_client_incluster(monkeypatch):
    """Test get_k8s_batch_v1_client with in-cluster config."""
    load_incluster = MagicMock()
    load_kube = MagicMock()
    batch_v1_api = MagicMock()

    monkeypatch.setattr(k8s_common.config, "load_incluster_config", load_incluster)
    monkeypatch.setattr(k8s_common.config, "load_kube_config", load_kube)
    monkeypatch.setattr(
        k8s_common.kubernetes.client, "BatchV1Api", lambda: batch_v1_api
    )

    # Simulate in-cluster config works (no exception)
    client = k8s_common.get_k8s_batch_v1_client()
    load_incluster.assert_called_once()
    load_kube.assert_not_called()
    assert client == batch_v1_api

def test_get_k8s_batch_v1_client_kubeconfig(monkeypatch):
    """Test get_k8s_batch_v1_client falls back to kubeconfig."""

    def raise_config_exception():
        raise k8s_common.config.ConfigException

    load_incluster = MagicMock(side_effect=raise_config_exception)
    load_kube = MagicMock()
    batch_v1_api = MagicMock()

    monkeypatch.setattr(k8s_common.config, "load_incluster_config", load_incluster)
    monkeypatch.setattr(k8s_common.config, "load_kube_config", load_kube)
    monkeypatch.setattr(
        k8s_common.kubernetes.client, "BatchV1Api", lambda: batch_v1_api
    )

    client = k8s_common.get_k8s_batch_v1_client()
    load_incluster.assert_called_once()
    load_kube.assert_called_once()
    assert client == batch_v1_api
