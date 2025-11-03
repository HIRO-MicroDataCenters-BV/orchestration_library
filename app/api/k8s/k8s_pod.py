"""
List pods in the cluster
"""

import logging
from uuid import UUID
from fastapi import APIRouter
from app.repositories.k8s import k8s_pod
from app.utils.helper import metrics
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
    pod_filters = build_pod_filters(
        namespace=namespace, name=name, pod_id=pod_id, status=status
    )
    return k8s_pod.list_k8s_pods(
        pod_filters=pod_filters, metrics_details=metrics("GET", "/k8s_pod")
    )


@router.delete("/")
def delete_pod(pod_id: UUID):
    """
    Delete a pods in the specified namespace.
    """

    return k8s_pod.delete_k8s_user_pod(
        pod_id=pod_id, metrics_details=metrics("DELETE", "/k8s_pod")
    )


@router.post("/recreate")
def recreate_pod(pod_id: UUID):
    """
    Recreate a pod by deleting and letting the controller recreate it.
    """

    return k8s_pod.recreate_k8s_user_pod(
        pod_id=pod_id, metrics_details=metrics("POST", "/k8s_pod/recreate")
    )


@router.get("/scale")
def scale_pod(pod_id: UUID, scale_type: k8s_pod.ScaleType, scale_delta: int = 1):
    """
    Scale a pod up or down.
    """

    return k8s_pod.scale_k8s_user_pod(
        pod_id=pod_id,
        scale_type=scale_type,
        scale_delta=scale_delta,
        metrics_details=metrics("GET", "/k8s_pod/scale"),
    )
