"""
List all nodes in the cluster.
"""

import time
from fastapi import APIRouter
from app.repositories.k8s import k8s_node


router = APIRouter(prefix="/k8s_node")


@router.get("/")
def list_all_nodes(name: str = None, node_id: str = None, status: str = None):
    """
    List all nodes in the cluster.
    If no filters are specified, list all nodes.
    """
    metrics_details = {
        "start_time": time.time(),
        "method": "GET",
        "endpoint": "/k8s_node",
    }
    return k8s_node.list_k8s_nodes(
        name=name, node_id=node_id, status=status, metrics_details=metrics_details
    )
