"""
CRUD operations for managing pods in the database.
This module provides functions to create, read, update, and delete pod records.
It uses SQLAlchemy ORM for database interactions.
"""

import re
from fastapi.responses import JSONResponse
from app.crud.k8s_common import K8S_IN_USE_NAMESPACE_REGEX, get_k8s_core_v1_client


def list_k8s_pods(
    namespace=None, name=None, pod_id=None, status=None, exclude_namespace_regex=None
):
    """
    List all pods in the specified namespace.
    If no namespace is specified, list all pods in all namespaces.
    """
    core_v1 = get_k8s_core_v1_client()
    print("Listing pods with their IPs:")

    if namespace:
        pods = core_v1.list_namespaced_pod(namespace, watch=False)
    else:
        # all namespaces
        pods = core_v1.list_pod_for_all_namespaces(watch=False)

    simplified_pods = []

    for pod in pods.items:
        # Apply filters if any are specified
        if name and pod.metadata.name != name:
            continue
        if pod_id and pod.metadata.uid != pod_id:
            continue
        if status and pod.status.phase != status:
            continue
        if namespace and pod.metadata.namespace != namespace:
            continue
        if exclude_namespace_regex and re.search(
            exclude_namespace_regex, pod.metadata.namespace
        ):
            continue
        simplified_pods.append(
            {
                "api_version": pod.api_version,
                "id": pod.metadata.uid,
                "namespace": pod.metadata.namespace,
                "name": pod.metadata.name,
                "labels": pod.metadata.labels,
                "annotations": pod.metadata.annotations,
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
        )
    return JSONResponse(content=simplified_pods)


def list_k8s_user_pods(namespace=None, name=None, pod_id=None, status=None):
    """
    List all pods excluding system pods in the specified namespace.
    If no namespace is specified, list all pods in all namespaces.
    """
    return list_k8s_pods(
        namespace=namespace,
        name=name,
        pod_id=pod_id,
        status=status,
        exclude_namespace_regex=K8S_IN_USE_NAMESPACE_REGEX,
    )
