from fastapi.responses import JSONResponse
import kubernetes.client
from kubernetes import client, config


def list_k8s_nodes(name=None, id=None, status=None):
    """
    List all nodes in the cluster.
    If no filters are specified, list all nodes.
    """
    
    try:
        # Load in-cluster configuration
        config.load_incluster_config()
    except config.ConfigException:
        # Fallback to local kubeconfig for development
        print("Falling back to load_kube_config for local development.")
        config.load_kube_config()

    coreV1 = kubernetes.client.CoreV1Api()
    print("Listing nodes with their details:")

    nodes = coreV1.list_node(watch=False)

    simplified_nodes = []

    for node in nodes.items:
        if name or id or status:
            # Apply filters if any are specified
            if name and node.metadata.name != name:
                continue
            if id and node.metadata.uid != id:
                continue
            if status and node.status.conditions[-1].type != status:
                continue
        simplified_nodes.append({
            "api_version": node.api_version,
            "id": node.metadata.uid,
            "name": node.metadata.name,
            "labels": node.metadata.labels,
            "annotations": node.metadata.annotations,
            "status": node.status.conditions[-1].type if node.status.conditions else None,
            "message": node.status.conditions[-1].message if node.status.conditions else None,
            "reason": node.status.conditions[-1].reason if node.status.conditions else None,
            "node_info": {
                "architecture": node.status.node_info.architecture,
                "container_runtime_version": node.status.node_info.container_runtime_version,
                "kernel_version": node.status.node_info.kernel_version,
                "kubelet_version": node.status.node_info.kubelet_version,
                "os_image": node.status.node_info.os_image,
            },
            "capacity": node.status.capacity,
            "allocatable": node.status.allocatable,
            "addresses": [
                {
                    "type": address.type,
                    "address": address.address,
                }
                for address in node.status.addresses
            ],
            "pod_cidrs": node.spec.pod_cidr,
            "taints": [
                {
                    "key": taint.key,
                    "value": taint.value,
                    "effect": taint.effect,
                }
                for taint in node.spec.taints
            ] if node.spec.taints else None,
            "unschedulable": node.spec.unschedulable,
        })

    return JSONResponse(content=simplified_nodes)