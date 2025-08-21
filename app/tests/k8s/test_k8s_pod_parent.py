"""
Tests for the get_parent_controller_details_of_pod function.
"""

import json
from unittest.mock import patch, MagicMock
import pytest
from kubernetes.client.rest import ApiException
from kubernetes.config import ConfigException

from app.repositories.k8s.k8s_pod_parent import get_parent_controller_details_of_pod
from app.tests.utils.mock_objects import mock_metrics_details, mock_user_pod, make_owner
from app.utils.exceptions import K8sAPIException, K8sConfigException, K8sValueError


# Mocking the Kubernetes client methods
# to avoid actual API calls during tests.
# The mock functions are used to simulate the behavior of the Kubernetes API.
# The actual functions are not used in the tests,
# so we prefix them with _ to silence pylint warnings.


@patch("app.repositories.k8s.k8s_pod_parent.get_k8s_core_v1_client")
@patch("app.repositories.k8s.k8s_pod_parent.get_k8s_apps_v1_client")
@patch("app.repositories.k8s.k8s_pod_parent.get_k8s_batch_v1_client")
def test_no_pod_name_or_id(_mock_batch, _mock_apps, _mock_core):
    """
    Test that ValueError is raised when neither pod_name nor pod_id is provided.
    """
    with pytest.raises(K8sValueError):
        get_parent_controller_details_of_pod(
            namespace="default", pod_name=None, pod_id=None
        )


@patch("app.repositories.k8s.k8s_pod_parent.get_k8s_core_v1_client")
@patch("app.repositories.k8s.k8s_pod_parent.get_k8s_apps_v1_client")
@patch("app.repositories.k8s.k8s_pod_parent.get_k8s_batch_v1_client")
def test_no_owner_references(_mock_batch, _mock_apps, mock_core):
    """
    Test that the function returns a message when the pod has no owner references.
    """
    mock_core.return_value.read_namespaced_pod.return_value = mock_user_pod()
    result = get_parent_controller_details_of_pod(
        namespace="default", pod_name="test-pod", pod_id=None
    )
    assert result["message"] == "Pod has no owner references (standalone pod)"


@patch("app.repositories.k8s.k8s_pod_parent.get_k8s_core_v1_client")
@patch("app.repositories.k8s.k8s_pod_parent.get_k8s_apps_v1_client")
@patch("app.repositories.k8s.k8s_pod_parent.get_k8s_batch_v1_client")
def test_deployment_parent(_mock_batch, mock_apps, mock_core):
    """
    Test that the function correctly identifies a Deployment as the parent controller.
    """
    # Setup pod with ReplicaSet owner
    owner = make_owner("ReplicaSet", "rs-name")
    m_pod = mock_user_pod()
    m_pod.metadata.owner_references = [owner]
    mock_core.return_value.read_namespaced_pod.return_value = m_pod

    # Setup ReplicaSet with Deployment owner
    rs = MagicMock()
    rs.metadata.owner_references = [make_owner("Deployment", "deploy-name")]
    mock_apps.return_value.read_namespaced_replica_set.return_value = rs

    # Setup Deployment
    deployment = MagicMock()
    deployment.metadata.name = "deploy-name"
    deployment.metadata.namespace = "default"
    deployment.api_version = "apps/v1"
    deployment.spec.replicas = 3
    mock_apps.return_value.read_namespaced_deployment.return_value = deployment

    metrics_details = mock_metrics_details("GET", "/k8s_pod_parent")
    response = get_parent_controller_details_of_pod(
        namespace="default",
        pod_name="test-pod",
        pod_id=None,
        metrics_details=metrics_details,
    )
    result = json.loads(response.body.decode())
    assert result["kind"] == "Deployment"
    assert result["name"] == "deploy-name"
    assert result["current_scale"] == 3


@patch("app.repositories.k8s.k8s_pod_parent.get_k8s_core_v1_client")
@patch("app.repositories.k8s.k8s_pod_parent.get_k8s_apps_v1_client")
@patch("app.repositories.k8s.k8s_pod_parent.get_k8s_batch_v1_client")
def test_statefulset_parent(_mock_batch, mock_apps, mock_core):
    """
    Test that the function correctly identifies a StatefulSet as the parent controller.
    """
    owner = make_owner("StatefulSet", "ss-name")
    m_pod = mock_user_pod()
    m_pod.metadata.owner_references = [owner]
    mock_core.return_value.read_namespaced_pod.return_value = m_pod

    statefulset = MagicMock()
    statefulset.metadata.name = "ss-name"
    statefulset.metadata.namespace = "default"
    statefulset.api_version = "apps/v1"
    statefulset.spec.replicas = 2
    mock_apps.return_value.read_namespaced_stateful_set.return_value = statefulset

    response = get_parent_controller_details_of_pod(
        namespace="default", pod_name="test-pod", pod_id=None
    )
    result = json.loads(response.body.decode())
    assert result["kind"] == "StatefulSet"
    assert result["name"] == "ss-name"
    assert result["current_scale"] == 2


@patch("app.repositories.k8s.k8s_pod_parent.get_k8s_core_v1_client")
@patch("app.repositories.k8s.k8s_pod_parent.get_k8s_apps_v1_client")
@patch("app.repositories.k8s.k8s_pod_parent.get_k8s_batch_v1_client")
def test_daemonset_parent(_mock_batch, mock_apps, mock_core):
    """
    Test that the function correctly identifies a DaemonSet as the parent controller.
    """
    owner = make_owner("DaemonSet", "ds-name")
    m_pod = mock_user_pod()
    m_pod.metadata.owner_references = [owner]
    mock_core.return_value.read_namespaced_pod.return_value = m_pod

    daemonset = MagicMock()
    daemonset.metadata.name = "ds-name"
    daemonset.metadata.namespace = "default"
    daemonset.api_version = "apps/v1"
    daemonset.status.desired_number_scheduled = 5
    mock_apps.return_value.read_namespaced_daemon_set.return_value = daemonset

    response = get_parent_controller_details_of_pod(
        namespace="default", pod_name="test-pod", pod_id=None
    )
    result = json.loads(response.body.decode())
    assert result["kind"] == "DaemonSet"
    assert result["name"] == "ds-name"
    assert result["current_scale"] == 5


@patch("app.repositories.k8s.k8s_pod_parent.get_k8s_core_v1_client")
@patch("app.repositories.k8s.k8s_pod_parent.get_k8s_apps_v1_client")
@patch("app.repositories.k8s.k8s_pod_parent.get_k8s_batch_v1_client")
def test_job_parent(mock_batch, _mock_apps, mock_core):
    """
    Test that the function correctly identifies a Job as the parent controller.
    """
    owner = make_owner("Job", "job-name")
    m_pod = mock_user_pod()
    m_pod.metadata.owner_references = [owner]
    mock_core.return_value.read_namespaced_pod.return_value = m_pod

    job = MagicMock()
    job.metadata.name = "job-name"
    job.metadata.namespace = "default"
    job.api_version = "batch/v1"
    job.spec.parallelism = 4
    mock_batch.return_value.read_namespaced_job.return_value = job

    response = get_parent_controller_details_of_pod(
        namespace="default", pod_name="test-pod", pod_id=None
    )
    result = json.loads(response.body.decode())
    assert result["kind"] == "Job"
    assert result["name"] == "job-name"
    assert result["current_scale"] == 4


@patch("app.repositories.k8s.k8s_pod_parent.get_k8s_core_v1_client")
@patch("app.repositories.k8s.k8s_pod_parent.get_k8s_apps_v1_client")
@patch("app.repositories.k8s.k8s_pod_parent.get_k8s_batch_v1_client")
def test_no_known_controller(_mock_batch, _mock_apps, mock_core):
    """
    Test that the function returns a message when the pod has an unknown controller.
    """
    owner = make_owner("UnknownKind", "unknown")
    m_pod = mock_user_pod()
    m_pod.metadata.owner_references = [owner]
    mock_core.return_value.read_namespaced_pod.return_value = m_pod

    result = get_parent_controller_details_of_pod(
        namespace="default", pod_name="test-pod", pod_id=None
    )
    assert "No known controller found" in result["message"]


@patch("app.repositories.k8s.k8s_pod_parent.get_k8s_core_v1_client")
@patch("app.repositories.k8s.k8s_pod_parent.get_k8s_apps_v1_client")
@patch("app.repositories.k8s.k8s_pod_parent.get_k8s_batch_v1_client")
def test_pod_by_id_not_found(_mock_batch, _mock_apps, mock_core):
    """
    Test that the function returns a message when no pod is found by UID.
    """
    # Simulate pod_id search with no match
    pod_list = MagicMock()
    pod_list.items = []
    mock_core.return_value.list_namespaced_pod.return_value = pod_list

    result = get_parent_controller_details_of_pod(
        namespace="default", pod_name=None, pod_id="notfound"
    )
    assert (
        "No pod found with name: None or UID: notfound in namespace: default"
        in result["message"]
    )


@patch("app.repositories.k8s.k8s_pod_parent.get_k8s_core_v1_client")
@patch("app.repositories.k8s.k8s_pod_parent.get_k8s_apps_v1_client")
@patch("app.repositories.k8s.k8s_pod_parent.get_k8s_batch_v1_client")
def test_pod_by_id_found(_mock_batch, mock_apps, mock_core):
    """
    Test that the function correctly retrieves a pod by UID.
    """
    owner = make_owner("DaemonSet", "ds-name")
    # Simulate pod_id search with a match
    pod = mock_user_pod()
    pod.metadata.uid = "found-uid"
    pod.metadata.owner_references = [owner]
    pod_list = MagicMock()
    pod_list.items = [pod]
    mock_core.return_value.list_namespaced_pod.return_value = pod_list

    daemonset = MagicMock()
    daemonset.metadata.name = "ds-name"
    daemonset.metadata.namespace = "default"
    daemonset.api_version = "apps/v1"
    daemonset.status.desired_number_scheduled = 2
    mock_apps.return_value.read_namespaced_daemon_set.return_value = daemonset

    response = get_parent_controller_details_of_pod(
        namespace="default", pod_name=None, pod_id="found-uid"
    )
    result = json.loads(response.body.decode())
    assert result["kind"] == "DaemonSet"
    assert result["name"] == "ds-name"
    assert result["current_scale"] == 2


@patch("app.repositories.k8s.k8s_pod_parent.get_k8s_core_v1_client")
def test_api_exception(mock_core):
    """Test that ApiException is handled and raises K8sAPIException."""
    mock_core.side_effect = ApiException("api error")
    with pytest.raises(K8sAPIException):
        get_parent_controller_details_of_pod(
            namespace="default", pod_name="pod", pod_id=None
        )


@patch("app.repositories.k8s.k8s_pod_parent.get_k8s_core_v1_client")
def test_config_exception(mock_core):
    """Test that ConfigException is handled and raises K8sConfigException."""
    mock_core.side_effect = ConfigException("config error")
    with pytest.raises(K8sConfigException):
        get_parent_controller_details_of_pod(
            namespace="default", pod_name="pod", pod_id=None
        )


@patch("app.repositories.k8s.k8s_pod_parent.get_k8s_core_v1_client")
def test_value_error(mock_core):
    """Test that ValueError is handled and raises K8sValueError."""
    mock_core.side_effect = ValueError("bad value")
    with pytest.raises(K8sValueError):
        get_parent_controller_details_of_pod(
            namespace="default", pod_name="pod", pod_id=None
        )
