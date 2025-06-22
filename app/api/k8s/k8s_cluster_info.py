"""
Cluster Info API
"""

from fastapi import APIRouter
from app.repositories.k8s import k8s_cluster_info


router = APIRouter(prefix="/k8s_cluster_info")


@router.get("/")
def get_cluster_info(advanced: bool = False):
    """
    Get cluster information about the Kubernetes cluster.
    If `advanced` is set to True, it will return detailed information.
    Otherwise, it will return basic information.

    :param advanced: If True, returns detailed cluster information.
    :return: A dictionary containing cluster information.
    """
    return k8s_cluster_info.get_cluster_info(advanced=advanced)
