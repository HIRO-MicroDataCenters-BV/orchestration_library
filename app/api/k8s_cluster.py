from fastapi import APIRouter
from app.crud import k8s_cluster
router = APIRouter(prefix="/k8s_node")
@router.get("/")
def list_cluster(name: str = None, id: str = None, status: str = None):
    """
    List the cluster information.
    If no filters are specified, list all cluster.
    """
    return k8s_cluster.list_cluster_info(name=name, id=id, status=status)