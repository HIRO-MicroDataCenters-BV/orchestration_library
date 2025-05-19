"""
CRUD operations for managing pods in the database.
This module provides functions to create, read, update, and delete pod records.
It uses SQLAlchemy ORM for database interactions.
"""

import re
from fastapi.responses import JSONResponse
from app.utils.k8s import get_pod_details
from app.repositories.k8s_common import K8S_IN_USE_NAMESPACE_REGEX, get_k8s_core_v1_client


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
        simplified_pods.append(get_pod_details(pod))
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
