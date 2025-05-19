"""
Utility functions for Kubernetes operations.
"""

def get_node_info(node):
    """
    Extracts and returns detailed information about a Kubernetes node.
    """
    return {
        "architecture": node.status.node_info.architecture,
        "container_runtime_version": node.status.node_info.container_runtime_version,
        "kernel_version": node.status.node_info.kernel_version,
        "kubelet_version": node.status.node_info.kubelet_version,
        "os_image": node.status.node_info.os_image,
    }

def get_node_basic_info(node):
    """
    Extracts and returns basic information about a Kubernetes node.
    """
    return {
        "name": node.metadata.name,
        "id": node.metadata.uid,
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
    }

def get_node_labels_annotations(node):
    """
    Extracts and returns labels and annotations of a Kubernetes node.
    """
    return {
        "labels": node.metadata.labels,
        "annotations": node.metadata.annotations,
    }

def get_node_details(node):
    """
    Extracts and returns detailed information about a Kubernetes node.
    """
    node_basic_info = get_node_basic_info(node)
    node_info = get_node_info(node)
    node_labels_annotations = get_node_labels_annotations(node)
    node_details = {
        "api_version": node.api_version,
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
    }
    # Combine all details into a single dictionary
    node_details.update(node_basic_info)
    node_details.update(node_labels_annotations)
    node_details["node_info"] = node_info
    return node_details

def get_pod_labels_annotations(pod):
    """
    Extracts and returns labels and annotations of a Kubernetes pod.
    """
    return {
        "labels": pod.metadata.labels,
        "annotations": pod.metadata.annotations,
    }

def get_pod_details(pod):
    """
    Extracts and returns detailed information about a Kubernetes pod.
    """
    pod_labels_annotations = get_pod_labels_annotations(pod)
    pod_details = {
        "api_version": pod.api_version,
        "id": pod.metadata.uid,
        "namespace": pod.metadata.namespace,
        "name": pod.metadata.name,
        "status": pod.status.phase,
        "message": pod.status.message,
        "reason": pod.status.reason,
        "host_ip": pod.status.host_ip,
        "pod_ip": pod.status.pod_ip,
        "start_time": str(pod.status.start_time),
        "node_name": pod.spec.node_name,
        "schedule_name": pod.spec.scheduler_name,
        "containers": [
            {
                "name": container.name,
                "image": container.image,
                "cpu_request": (
                    container.resources.requests.get("cpu")
                    if container.resources.requests
                    else None
                ),
                "memory_request": (
                    container.resources.requests.get("memory")
                    if container.resources.requests
                    else None
                ),
                "cpu_limit": (
                    container.resources.limits.get("cpu")
                    if container.resources.limits
                    else None
                ),
                "memory_limit": (
                    container.resources.limits.get("memory")
                    if container.resources.limits
                    else None
                ),
            }
            for container in pod.spec.containers
        ],
    }
    # Combine all details into a single dictionary
    pod_details.update(pod_labels_annotations)
    return pod_details

def get_pod_basic_info(pod):
    """
    Extracts and returns basic information about a Kubernetes pod.
    """
    return {
        "id": pod.metadata.uid,
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
