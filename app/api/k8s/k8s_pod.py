"""
List pods in the cluster
"""
import logging
from fastapi import APIRouter
from app.repositories.k8s import k8s_pod

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/k8s_pod")


@router.get("/")
def list_all_pods(
    namespace: str = None, name: str = None, pod_id: str = None, status: str = None
):
    """
    List all pods in the specified namespace.
    If no namespace is specified, list all pods in all namespaces.
    """
    return k8s_pod.list_k8s_pods(
        namespace=namespace, name=name, pod_id=pod_id, status=status
    )
