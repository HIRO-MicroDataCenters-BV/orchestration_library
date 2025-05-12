"""
List pods in the cluster
"""

from fastapi import APIRouter
from app.crud import k8s_pod


router = APIRouter(prefix="/k8s_user_pod")


@router.get("/")
def list_all_user_pods(
    namespace: str = None, name: str = None, pod_id: str = None, status: str = None
):
    """
    List all pods excluding system pods in the specified namespace.
    If no namespace is specified, list all pods in all namespaces.
    """
    return k8s_pod.list_k8s_user_pods(namespace=namespace, name=name, pod_id=pod_id, status=status)
