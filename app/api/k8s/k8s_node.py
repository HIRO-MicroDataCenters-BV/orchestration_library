"""
List all nodes in the cluster.
"""
from fastapi import APIRouter
from app.repositories import k8s_node



router = APIRouter(prefix="/k8s_node")
@router.get("/")
def list_all_nodes(name: str = None, node_id: str = None, status: str = None):
    """
    List all nodes in the cluster.
    If no filters are specified, list all nodes.
    """
    return k8s_node.list_k8s_nodes(name=name, node_id=node_id, status=status)
