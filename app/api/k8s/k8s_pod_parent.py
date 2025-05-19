"""
Get the parent controller of a Kubernetes pod.
This module provides a function to retrieve the parent controller
of a Kubernetes pod, which can be a Deployment, StatefulSet, DaemonSet, or Job.
It uses the Kubernetes API to fetch the necessary details.
"""

from fastapi import APIRouter

from app.repositories.k8s import k8s_pod_parent


router = APIRouter(prefix="/k8s_pod_parent")


@router.get("/")
def get_pod_parent(namespace: str, name: str = None, pod_id: str = None):
    """
    Get the parent controller of a Kubernetes pod.
    Args:
        namespace (str): Namespace of the pod.
        name (str): Name of the pod.
        pod_id (str): UID of the pod.
    Returns:
        dict: Details of the parent controller (Deployment, StatefulSet, DaemonSet, or Job).
    """
    return k8s_pod_parent.get_parent_controller_details_of_pod(
        namespace=namespace, pod_name=name, pod_id=pod_id
    )
