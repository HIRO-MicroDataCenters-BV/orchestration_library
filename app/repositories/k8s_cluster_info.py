"""
Get cluster information from Kubernetes.
"""

from kubernetes.client.exceptions import ApiException

from app.repositories.k8s_common import (get_k8s_core_v1_client, 
                                         get_k8s_version_api_client)
from app.utils.k8s import get_node_details, get_pod_details


def get_cluster_info():
    """
    Fetches and returns basic information about the Kubernetes cluster.
    """
    core_v1 = get_k8s_core_v1_client()
    version_v1 = get_k8s_version_api_client()

    # Version info
    version_info = version_v1.get_code()

    # Get cluster nodes
    try:
        nodes = core_v1.list_node().items
    except ApiException as e:
        nodes = []
        print(f"Error fetching nodes: {e}")

    # Get cluster components
    try:
        components = core_v1.list_component_status().items
    except ApiException as e:
        components = []
        print(f"Error fetching components: {e}")

    # Get kube-system pods
    try:
        kube_system_pods = core_v1.list_namespaced_pod(namespace="kube-system").items
    except ApiException as e:
        kube_system_pods = []
        print(f"Error fetching kube-system pods: {e}")

    node_infos = []
    for node in nodes:
        node_infos.append(get_node_details(node))

    component_status = []
    for comp in components:
        component_status.append(
            {
                "name": comp.metadata.name,
                "conditions": [
                    {"type": cond.type, "status": cond.status} for cond in comp.conditions
                ],
            }
        )

    kube_system_pods_info = []
    for pod in kube_system_pods:
        kube_system_pods_info.append(get_pod_details(pod))

    cluster_info = {
        "kubernetes_version": version_info.git_version,
        "nodes": node_infos,
        "components": component_status,
        "kube_system_pods": kube_system_pods_info,
        "cluster_id": version_info.git_commit,
        "cluster_name": version_info.git_version.split("-")[0],
        "cluster_domain": (
            version_info.git_version.split("-")[1]
            if "-" in version_info.git_version
            else None
        ),
        "cluster_ip": (
            version_info.git_version.split("-")[2]
            if "-" in version_info.git_version
            else None
        ),
    }

    return cluster_info
