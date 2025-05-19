"""
Cluster Info API
"""

from fastapi import APIRouter
from app.repositories import k8s_cluster_info


router = APIRouter(prefix="/k8s_cluster_info")


@router.get("/")
def get_cluster_info():
    """
    Get basic information about the Kubernetes cluster.
    This includes version info, nodes, components, and kube-system pods.
    """
    return k8s_cluster_info.get_cluster_info()
