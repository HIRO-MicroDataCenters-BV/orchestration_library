"""
Operations on Kubernetes nodes.
This module provides functions to list nodes in the cluster.
"""

from fastapi.responses import JSONResponse
from kubernetes import client
from kubernetes.config import ConfigException
from kubernetes.client.rest import ApiException

from app.repositories.k8s.k8s_common import (
    get_k8s_core_v1_client,
    get_k8s_custom_objects_client,
)
from app.utils.k8s import get_node_details, handle_k8s_exceptions


# Suppress R1710: All exception handlers call a function that always raises, so no return needed.
# pylint: disable=R1710
def list_k8s_nodes(name=None, node_id=None, status=None) -> JSONResponse:
    """
    List all nodes in the Kubernetes cluster with optional filters.
    :param name: Filter by node name.
    :param node_id: Filter by node ID (UID).
    :param status: Filter by node status (e.g., "Ready", "NotReady").
    :return: A list of nodes with their details.
    """
    try:
        return JSONResponse(content=get_k8s_nodes(name, node_id, status))
    except ApiException as e:
        handle_k8s_exceptions(e, context_msg="Kubernetes API error while listing nodes")
    except ConfigException as e:
        handle_k8s_exceptions(
            e, context_msg="Kubernetes configuration error while listing nodes"
        )
    except ValueError as e:
        handle_k8s_exceptions(e, context_msg="Value error while listing nodes")


def get_k8s_nodes(name=None, node_id=None, status=None):
    """
    List all nodes in the cluster.
    If no filters are specified, list all nodes.
    """
    core_v1 = get_k8s_core_v1_client()
    print("Listing nodes with their details:")

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
        node_details["usage"] = usage
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
            print(
                "Warning: Metrics server not installed or not available. "
                "Node metrics will be empty."
            )
        else:
            print(f"Failed to fetch node metrics: {e}")
        return {}
