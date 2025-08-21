"""
Cluster Info API
"""

import time
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
    metrics_details = {
        "start_time": time.time(),
        "method": "GET",
        "endpoint": "/k8s_cluster_info",
    }
    return k8s_cluster_info.get_cluster_info(
        advanced=advanced, metrics_details=metrics_details
    )
