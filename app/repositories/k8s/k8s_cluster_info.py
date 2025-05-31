"""
Get cluster information from Kubernetes.
"""

import boto3
from kubernetes.client.exceptions import ApiException
from kubernetes import config

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

    # Get cluster id
    try:
        # The cluster ID is typically the UID of the kube-system namespace
        cluster_id = core_v1.read_namespace(name="kube-system").metadata.uid
    except ApiException as e:
        cluster_id = None
        print(f"Error fetching cluster ID: {e}")

    # # Get cluster name
    # try:
    #     config.load_incluster_config()
    #     contexts, active_context = config.list_kube_config_contexts()
    #     print(f"Contexts: {contexts}")
    #     print(f"Active context: {active_context}")
    #     cluster_name = active_context['context']['cluster']
    # except config.ConfigException as e:
    #     cluster_name = None
    #     print(f"Error fetching cluster name: {e}")


    cluster_info = {
        "kubernetes_version": version_info.git_version,
        "nodes": nodes,
        "components": component_status,
        "kube_system_pods": kube_system_pods_info,
        "cluster_id": cluster_id,
        "cluster_name": cluster_name,
    }

    return cluster_info
