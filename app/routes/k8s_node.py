from fastapi import APIRouter
from app.crud import k8s_node



router = APIRouter(prefix="/k8s_node")
@router.get("/")
def list_all_nodes(name: str = None, id: str = None, status: str = None):
    """
    List all nodes in the cluster.
    If no filters are specified, list all nodes.
    """
    return k8s_node.list_k8s_nodes(name=name, id=id, status=status)
    
