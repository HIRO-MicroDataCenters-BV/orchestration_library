"""
Cluster statistic Info API
"""

from fastapi import APIRouter
from app.repositories.k8s import k8s_cluster_info


router = APIRouter(prefix="/ui_cluster_info")


@router.get("/")
def get_ui_cluster_statistic_info():
    """
    Get statistic data from cluster and other APIS
    """
    return k8s_cluster_info.get_cluster_info()