"""
Operations on Kubernetes nodes.
This module provides functions to list nodes in the cluster.
"""

import logging
from fastapi.responses import JSONResponse
from kubernetes import client
from kubernetes.config import ConfigException
from kubernetes.client.rest import ApiException

from app.metrics.helper import record_k8s_node_metrics
from app.repositories.k8s.k8s_common import (
    get_k8s_core_v1_client,
    get_k8s_custom_objects_client,
)
from app.utils.k8s import get_node_details, handle_k8s_exceptions, parse_cpu_to_cores, parse_memory_to_bytes

logger = logging.getLogger(__name__)


# Suppress R1710: All exception handlers call a function that always raises, so no return needed.
# pylint: disable=R1710
def list_k8s_nodes(
    name=None, node_id=None, status=None, metrics_details=None
) -> JSONResponse:
    """
    List all nodes in the Kubernetes cluster with optional filters.
    :param name: Filter by node name.
    :param node_id: Filter by node ID (UID).
    :param status: Filter by node status (e.g., "Ready", "NotReady").
    :return: A list of nodes with their details.
    """
    try:
        simplified_nodes = get_k8s_nodes(name, node_id, status)
        record_k8s_node_metrics(
            metrics_details=metrics_details,
            status_code=200,
        )
        return JSONResponse(content=simplified_nodes)
    except ApiException as e:
        handle_k8s_exceptions(
            e,
            context_msg="Kubernetes API error while listing nodes",
            metrics_details=metrics_details,
        )
    except ConfigException as e:
        handle_k8s_exceptions(
            e,
            context_msg="Kubernetes configuration error while listing nodes",
            metrics_details=metrics_details,
        )
    except ValueError as e:
        handle_k8s_exceptions(
            e,
            context_msg="Value error while listing nodes",
            metrics_details=metrics_details,
        )


def get_k8s_nodes(name=None, node_id=None, status=None):
    """
    List all nodes in the cluster.
    If no filters are specified, list all nodes.
    """
    core_v1 = get_k8s_core_v1_client()
    logger.info("Listing nodes with their details:")

    # Get node metrics from metrics.k8s.io API
    node_metrics_map = get_k8s_node_metric_map()
    nodes = core_v1.list_node(watch=False)

    simplified_nodes = []

    for node in nodes.items:
        if name or node_id or status:
            # Apply filters if any are specified
            if name and node.metadata.name != name:
                continue
            if node_id and node.metadata.uid != node_id:
                continue
            if status and node.status.conditions[-1].type != status:
                continue
        # Simplify node details
        usage = node_metrics_map.get(node.metadata.name, {}).get("usage", {})
        node_details = get_node_details(node)
        # Compute utilization
        cpu_allocatable = node_details.get("allocatable", {}).get("cpu")
        mem_allocatable = node_details.get("allocatable", {}).get("memory")
        cpu_usage = usage.get("cpu")
        mem_usage = usage.get("memory")

        cpu_util_pct = compute_cpu_utilization(cpu_usage, cpu_allocatable)
        mem_util_pct = compute_memory_utilization(mem_usage, mem_allocatable)

        node_details["usage"] = usage
        node_details["utilization"] = {
            "cpu": cpu_util_pct,
            "memory": mem_util_pct,
        }
        simplified_nodes.append(node_details)
    return simplified_nodes


def get_k8s_node_metric_map():
    """
    Get a map of node names to their metrics.
    :return: A dictionary mapping node names to their metrics.
    """
    custom_api = get_k8s_custom_objects_client()
    try:
        node_metrics = custom_api.list_cluster_custom_object(
            group="metrics.k8s.io", version="v1beta1", plural="nodes"
        )
        return {item["metadata"]["name"]: item for item in node_metrics["items"]}
    except client.rest.ApiException as e:
        if e.status == 404:
            logger.warning(
                "Warning: Metrics server not installed or not available. "
                "Node metrics will be empty."
            )
        else:
            logger.error("Failed to fetch node metrics: %s", e)
        return {}

def compute_cpu_utilization(usage, capacity):
    """
    usage: e.g. '2059539221n' (nanocores) or '2500m'
    capacity: e.g. '16' (cores) or '16000m'
    """
    try:
        usage_cores = parse_cpu_to_cores(usage)
        capacity_cores = parse_cpu_to_cores(capacity)
        if capacity_cores == 0:
            return None
        return round((usage_cores / capacity_cores) * 100, 2)
    except Exception:  # noqa: BLE001
        return None


def compute_memory_utilization(usage, capacity):
    """
    usage/capacity like '10119376Ki', '48731292Ki'
    """
    try:
        usage_bytes = parse_memory_to_bytes(usage)
        capacity_bytes = parse_memory_to_bytes(capacity)
        if capacity_bytes == 0:
            return None
        return round((usage_bytes / capacity_bytes) * 100, 2)
    except Exception:  # noqa: BLE001
        return None
