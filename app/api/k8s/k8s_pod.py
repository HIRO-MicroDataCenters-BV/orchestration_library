"""
List pods in the cluster
"""
import logging
import time
from uuid import UUID
from fastapi import APIRouter
from app.repositories.k8s import k8s_pod
from app.utils.k8s import build_pod_filters

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/k8s_pod")


@router.get("/")
def list_all_pods(
    namespace: str = None, name: str = None, pod_id: str = None, status: str = None
):
    """
    List all pods in the specified namespace.
    If no namespace is specified, list all pods in all namespaces.
    """
    metrics_details = {
        "start_time": time.time(),
        "method": "GET",
        "endpoint": "/k8s_pod",
    }
    pod_filters = build_pod_filters(
        namespace=namespace, name=name, pod_id=pod_id, status=status
    )
    return k8s_pod.list_k8s_pods(
        pod_filters=pod_filters, metrics_details=metrics_details
    )

@router.delete("/")
def delete_pod(
    pod_id: UUID
):
    """
    Delete a pods in the specified namespace.
    """
    metrics_details = {
        "start_time": time.time(),
        "method": "DELETE",
        "endpoint": "/k8s_pod",
    }

    return k8s_pod.delete_k8s_user_pod(
        pod_id=pod_id, metrics_details=metrics_details
    )

@router.post("/recreate")
def recreate_pod(
    pod_id: UUID
):
    """
    Recreate a pod by deleting and letting the controller recreate it.
    """
    metrics_details = {
        "start_time": time.time(),
        "method": "POST",
        "endpoint": "/k8s_pod/recreate",
    }

    return k8s_pod.recreate_k8s_user_pod(
        pod_id=pod_id, metrics_details=metrics_details
    )
