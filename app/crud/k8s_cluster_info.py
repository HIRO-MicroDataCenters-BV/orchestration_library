"""
Get cluster information from Kubernetes.
"""

from kubernetes.client.exceptions import ApiException

from app.crud.k8s_common import get_k8s_core_v1_client, get_k8s_version_api_client


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
        node_infos.append(
            {
                "name": node.metadata.name,
                "uid": node.metadata.uid,
                "status": (
                    node.status.conditions[-1].type if node.status.conditions else None
                ),
                "message": (
                    node.status.conditions[-1].message
                    if node.status.conditions
                    else None
                ),
                "reason": (
                    node.status.conditions[-1].reason
                    if node.status.conditions
                    else None
                ),
                "node_info": {
                    "architecture": node.status.node_info.architecture,
                    "container_runtime_version": node.status.node_info.container_runtime_version,
                    "kernel_version": node.status.node_info.kernel_version,
                    "kubelet_version": node.status.node_info.kubelet_version,
                    "os_image": node.status.node_info.os_image,
                },
                "annotations": node.metadata.annotations,
                "labels": node.metadata.labels,
                "capacity": node.status.capacity,
                "allocatable": node.status.allocatable,
                "taints": (
                    [
                        {"key": taint.key, "value": taint.value, "effect": taint.effect}
                        for taint in node.spec.taints or []
                    ]
                    if node.spec.taints
                    else None
                ),
                "unschedulable": node.spec.unschedulable,
            }
        )

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
        kube_system_pods_info.append(
            {
                "name": pod.metadata.name,
                "namespace": pod.metadata.namespace,
                "phase": pod.status.phase,
                "node_name": pod.spec.node_name,
                "containers": [
                    {
                        "name": c.name,
                        "ready": c.ready,
                        "restart_count": c.restart_count,
                        "image": c.image,
                    }
                    for c in pod.status.container_statuses or []
                ],
            }
        )

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
