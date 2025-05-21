"""
Operations on Kubernetes nodes.
This module provides functions to list nodes in the cluster.
"""
from fastapi.responses import JSONResponse
from kubernetes import client

from app.repositories.k8s.k8s_common import (get_k8s_core_v1_client,
                                 get_k8s_custom_objects_client)
from app.utils.k8s import get_node_details


def list_k8s_nodes(name=None, node_id=None, status=None):
    """
    List all nodes in the cluster.
    If no filters are specified, list all nodes.
    """
    core_v1 = get_k8s_core_v1_client()
    custom_api = get_k8s_custom_objects_client()
    print("Listing nodes with their details:")

    # Get node metrics from metrics.k8s.io API
    node_metrics_map = {}
    try:
        node_metrics = custom_api.list_cluster_custom_object(
            group="metrics.k8s.io",
            version="v1beta1",
            plural="nodes"
        )
        node_metrics_map = {item["metadata"]["name"]: item for item in node_metrics["items"]}
    except client.rest.ApiException as e:
        print(f"Failed to fetch node metrics: {e}")

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

    return JSONResponse(content=simplified_nodes)
