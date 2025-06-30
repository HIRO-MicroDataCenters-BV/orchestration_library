# -*- coding: utf-8 -*-
"""
Utility functions for Kubernetes operations.
This module provides functions to extract and format information from Kubernetes nodes and pods,
as well as handle exceptions related to Kubernetes API and configuration.
"""
from collections.abc import Mapping, Iterable
from kubernetes import client, config
from app.utils.exceptions import K8sAPIException, K8sConfigException, K8sValueError

def to_serializable(obj):
    """Recursively convert an object to a JSON-serializable format."""
    if isinstance(obj, (str, int, float, bool, type(None))):
        return obj

    if isinstance(obj, Mapping):
        return {k: to_serializable(v) for k, v in obj.items()}

    if isinstance(obj, Iterable) and not isinstance(obj, (str, bytes)):
        return [to_serializable(item) for item in obj]

    if hasattr(obj, "__dict__"):
        return {k: to_serializable(v) for k, v in vars(obj).items() if not k.startswith("_")}

    if hasattr(obj, "__slots__"):
        return {slot: to_serializable(getattr(obj, slot)) for slot in obj.__slots__}

    return str(obj)

def get_node_info(node):
    """
    Extracts and returns detailed information about a Kubernetes node.
    """
    return {
        "architecture": node.status.node_info.architecture,
        "container_runtime_version": node.status.node_info.container_runtime_version,
        "kernel_version": node.status.node_info.kernel_version,
        "kubelet_version": node.status.node_info.kubelet_version,
        "os_image": node.status.node_info.os_image,
    }

def get_node_basic_info(node):
    """
    Extracts and returns basic information about a Kubernetes node.
    """
    return {
        "name": node.metadata.name,
        "id": node.metadata.uid,
        "status": (
            node.status.conditions[-1].type if node.status.conditions else None
        ),
        "message": (
            node.status.conditions[-1].message
            if node.status.conditions
            else None
        ),
        "reason": (
            node.status.conditions[-1].reason
            if node.status.conditions
            else None
        ),
    }

def get_node_labels_annotations(node):
    """
    Extracts and returns labels and annotations of a Kubernetes node.
    """
    return {
        "labels": node.metadata.labels,
        "annotations": node.metadata.annotations,
    }

def get_node_details(node):
    """
    Extracts and returns detailed information about a Kubernetes node.
    """
    node_basic_info = get_node_basic_info(node)
    node_info = get_node_info(node)
    node_labels_annotations = get_node_labels_annotations(node)
    node_details = {
        "api_version": node.api_version,
        "capacity": node.status.capacity,
        "allocatable": node.status.allocatable,
        "addresses": [
            {
                "type": address.type,
                "address": address.address,
            }
            for address in node.status.addresses
        ],
        "pod_cidrs": node.spec.pod_cidr,
        "taints": [
            {
                "key": taint.key,
                "value": taint.value,
                "effect": taint.effect,
            }
            for taint in node.spec.taints
        ] if node.spec.taints else None,
        "unschedulable": node.spec.unschedulable,
    }
    # Combine all details into a single dictionary
    node_details.update(node_basic_info)
    node_details.update(node_labels_annotations)
    node_details["node_info"] = node_info
    return node_details

def get_pod_labels_annotations(pod):
    """
    Extracts and returns labels and annotations of a Kubernetes pod.
    """
    return {
        "labels": pod.metadata.labels if pod and pod.metadata else {},
        "annotations": pod.metadata.annotations if pod and pod.metadata else {},
    }

def get_pod_details(pod):
    """
    Extracts and returns detailed information about a Kubernetes pod.
    """
    pod_labels_annotations = get_pod_labels_annotations(pod)
    pod_details = {
        "api_version": pod.api_version,
        "id": pod.metadata.uid if pod.metadata else None,
        "namespace": pod.metadata.namespace if pod.metadata else None,
        "name": pod.metadata.name if pod.metadata else None,
        "status": pod.status.phase if pod.status else None,
        "message": pod.status.message if pod.status else None,
        "reason": pod.status.reason if pod.status else None,
        "host_ip": pod.status.host_ip if pod.status else None,
        "pod_ip": pod.status.pod_ip if pod.status else None,
        "start_time": str(pod.status.start_time) if pod.status else None,
        "node_name": pod.spec.node_name if pod.spec else None,
        "schedule_name": pod.spec.scheduler_name if pod.spec else None,
        "containers": [
            {
                "name": container.name,
                "image": container.image,
                "cpu_request": (
                    container.resources.requests.get("cpu")
                    if container.resources.requests
                    else None
                ),
                "memory_request": (
                    container.resources.requests.get("memory")
                    if container.resources.requests
                    else None
                ),
                "cpu_limit": (
                    container.resources.limits.get("cpu")
                    if container.resources.limits
                    else None
                ),
                "memory_limit": (
                    container.resources.limits.get("memory")
                    if container.resources.limits
                    else None
                ),
            }
            for container in pod.spec.containers or []
        ],
    }
    # Combine all details into a single dictionary
    pod_details.update(pod_labels_annotations)
    return pod_details

def get_pod_basic_info(pod):
    """
    Extracts and returns basic information about a Kubernetes pod.
    """
    return {
        "id": pod.metadata.uid if pod.metadata else None,
        "name": pod.metadata.name if pod.metadata else None,
        "namespace": pod.metadata.namespace if pod.metadata else None,
        "phase": pod.status.phase if pod.status else None,
        "node_name": pod.spec.node_name if pod.spec else None,
        "containers": [
            {
                "name": c.name,
                "ready": c.ready,
                "restart_count": c.restart_count,
                "image": c.image,
            }
            for c in pod.status.container_statuses or []
        ],
    }

def get_deployment_basic_info(dep):
    """
    Extracts and returns basic information about a Kubernetes deployment.
    """
    return {
        "name": dep.metadata.name,
        "namespace": dep.metadata.namespace,
        "labels": dep.metadata.labels,
        "replicas": dep.spec.replicas,
        "available_replicas": getattr(dep.status, "available_replicas", None),
    }

def get_job_basic_info(job):
    """
    Extracts and returns basic information about a Kubernetes job.
    """
    return {
        "name": job.metadata.name,
        "namespace": job.metadata.namespace,
        "labels": job.metadata.labels,
        "active": getattr(job.status, "active", None),
        "succeeded": getattr(job.status, "succeeded", None),
        "failed": getattr(job.status, "failed", None),
    }

def get_statefulset_basic_info(sts):
    """
    Extracts and returns basic information about a Kubernetes statefulset.
    """
    return {
        "name": sts.metadata.name,
        "namespace": sts.metadata.namespace,
        "labels": sts.metadata.labels,
        "replicas": sts.spec.replicas,
        "ready_replicas": getattr(sts.status, "ready_replicas", None),
    }

def get_daemonset_basic_info(ds):
    """
    Extracts and returns basic information about a Kubernetes daemonset.
    """
    return {
        "name": ds.metadata.name,
        "namespace": ds.metadata.namespace,
        "labels": ds.metadata.labels,
        "desired_number_scheduled": getattr(ds.status, "desired_number_scheduled", None),
        "number_ready": getattr(ds.status, "number_ready", None),
    }

def handle_k8s_exceptions(e, context_msg, details=None):
    """
    Handles exceptions raised by Kubernetes API or configuration issues.
    Raises specific exceptions based on the type of error.
    """
    if isinstance(e, client.rest.ApiException):
        raise K8sAPIException(f"{context_msg}: {str(e)}", details=details or str(e))
    if isinstance(e, config.ConfigException):
        raise K8sConfigException(f"{context_msg}: {str(e)}", details=details or str(e))
    if isinstance(e, ValueError):
        raise K8sValueError(f"{context_msg}: {str(e)}", details=details or str(e))
    raise e  # re-raise unexpected exceptions
