"""
Get cluster information from Kubernetes.
"""

from kubernetes.client.exceptions import ApiException

from app.repositories.k8s.k8s_common import (get_k8s_core_v1_client,
                                         get_k8s_version_api_client)
from app.repositories.k8s.k8s_node import get_k8s_nodes
from app.utils.k8s import get_pod_basic_info


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
        nodes = get_k8s_nodes()
        print(f"Fetched {nodes}")
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
        kube_system_pods_info.append(get_pod_basic_info(pod))

    cluster_info = {
        "kubernetes_version": version_info.git_version,
        "nodes": nodes,
        "components": component_status,
        "kube_system_pods": kube_system_pods_info,
        "cluster_id": version_info.git_commit
    }

    return cluster_info
