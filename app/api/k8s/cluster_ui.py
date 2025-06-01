"""
Cluster statistic Info API
"""

from fastapi import APIRouter
from app.api import pod
from app.repositories.k8s import k8s_cluster_info

router = APIRouter(prefix="/ui_cluster_info")


@router.get("/")
def get_ui_cluster_statistic_info():
    """
    Get statistic data from cluster and other APIS
    """
    cluster_info = k8s_cluster_info.get_cluster_info()

    """
    loop the nodes of the cluster , get each node usage, and calculate the cluster usage
    """
    cluster_cpu_usage = 0
    cluster_memory_usage = 0
    cluster_cpu_availability = 0
    cluster_memory_availability = 0

    for node in cluster_info.get("nodes", []):
        node_usage = node.get("usage", {})
        cpu_str = node_usage.get("cpu", "0")
        mem_str = node_usage.get("memory", "0")
        cluster_cpu_usage += parse_cpu(cpu_str)
        cluster_memory_usage += parse_memory(mem_str)
        node_allocatable = node.get("allocatable", {})
        cluster_cpu_availability += parse_cpu(node_allocatable.get("cpu", "0"))
        cluster_memory_availability += parse_memory(node_allocatable.get("memory", "0"))
    
    # calculate cpu and memory utilization
    cluster_cpu_usage = round(cluster_cpu_usage, 2)  # in millicores
    cluster_memory_usage = round(cluster_memory_usage, 2)  # in Mi
    cluster_cpu_availability = round(cluster_cpu_availability, 2)  # in millicores
    cluster_memory_availability = round(cluster_memory_availability, 2)  # in Mi
    if cluster_cpu_availability > 0:
        cluster_cpu_utilization = round((cluster_cpu_usage / cluster_cpu_availability) * 100, 2)
    else:
        cluster_cpu_utilization = 0.0
    if cluster_memory_availability > 0:
        cluster_memory_utilization = round((cluster_memory_usage / cluster_memory_availability) * 100, 2)
    else:
        cluster_memory_utilization = 0.0


    cluster_statistic_info = {
        "cluster_info": cluster_info,
        "cluster_cpu_usage": cluster_cpu_usage,
        "cluster_memory_usage": cluster_memory_usage,
        "cluster_cpu_availability": cluster_cpu_availability,
        "cluster_memory_availability": cluster_memory_availability,
        "cluster_cpu_utilization": cluster_cpu_utilization,
        "cluster_memory_utilization": cluster_memory_utilization
    }

    return cluster_statistic_info

def parse_cpu(cpu_str):
    # Parses CPU string like "448007813n" to millicores (m)
    if cpu_str.endswith("n"):
        return int(cpu_str[:-1]) / 1_000_000  # nanocores to millicores
    elif cpu_str.endswith("u"):
        return int(cpu_str[:-1]) / 1_000      # microcores to millicores
    elif cpu_str.endswith("m"):
        return int(cpu_str[:-1])              # already in millicores
    else:
        return int(cpu_str) * 1000            # assume cores, convert to millicores

def parse_memory(mem_str):
    # Parses memory string like "13459572Ki" to Mi
    units = {"Ki": 1/1024, "Mi": 1, "Gi": 1024}
    for unit, factor in units.items():
        if mem_str.endswith(unit):
            return int(mem_str[:-len(unit)]) * factor
    return int(mem_str) / (1024 * 1024)  # bytes to Mi
