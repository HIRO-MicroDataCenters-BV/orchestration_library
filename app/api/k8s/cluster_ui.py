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
    k8s_cluster_info.cluster_info = k8s_cluster_info.get_cluster_info()

    """
    loop the nodes of the cluster , get each node usage, and calculate the cluster usage
    """
    cluster_usage = 0;


    cluster_statistic_info = {
        "cluster_info": k8s_cluster_info.cluster_info,
        "cluster_usage": cluster_usage
    }



    return cluster_statistic_info;
