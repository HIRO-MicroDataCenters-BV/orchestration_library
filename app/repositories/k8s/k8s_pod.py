"""
List the pods in the Kubernetes cluster.
"""

import json
import logging
import re
from fastapi.responses import JSONResponse
from kubernetes.client.rest import ApiException
from kubernetes.config import ConfigException
from app.metrics.helper import record_k8s_pod_metrics
from app.utils.k8s import get_pod_details, handle_k8s_exceptions
from app.repositories.k8s.k8s_common import (
    get_k8s_core_v1_client,
)
from app.utils.constants import K8S_IN_USE_NAMESPACE_REGEX

logger = logging.getLogger(__name__)


# Suppress R1710: All exception handlers call a function that always raises, so no return needed.
# pylint: disable=R1710
def list_k8s_pods(pod_filters=None, metrics_details=None) -> JSONResponse:
    """
    List all pods in the specified namespace.
    If no namespace is specified, list all pods in all namespaces.
    """
    try:
        namespace = pod_filters.get("namespace") if pod_filters else None
        name = pod_filters.get("name") if pod_filters else None
        pod_id = pod_filters.get("pod_id") if pod_filters else None
        status = pod_filters.get("status") if pod_filters else None
        exclude_namespace_regex = (
            pod_filters.get("exclude_namespace_regex") if pod_filters else None
        )

        core_v1 = get_k8s_core_v1_client()
        logger.info("Listing pods with their IPs:")

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
        record_k8s_pod_metrics(
            metrics_details=metrics_details,
            status_code=200,
        )
        return JSONResponse(content=simplified_pods)
    except ApiException as e:
        handle_k8s_exceptions(e, context_msg="Kubernetes API error while listing pods")
    except ConfigException as e:
        handle_k8s_exceptions(
            e, context_msg="Kubernetes configuration error while listing pods"
        )
    except ValueError as e:
        handle_k8s_exceptions(e, context_msg="Value error while listing pods")


def list_k8s_user_pods(pod_filters=None, metrics_details=None):
    """
    List all pods excluding system pods in the specified namespace.
    If no namespace is specified, list all pods in all namespaces.
    """
    pod_filters["exclude_namespace_regex"] = K8S_IN_USE_NAMESPACE_REGEX
    return list_k8s_pods(
        pod_filters=pod_filters,
        metrics_details=metrics_details,
    )

def delete_k8s_user_pod(pod_id, metrics_details=None) -> JSONResponse:
    """
    Delete a pod by pod_id (UID). Will not delete system pods.
    """
    try:
        # Find the pod details using the pod_id
        pod_filters = {"pod_id": str(pod_id)}
        response = list_k8s_user_pods(pod_filters=pod_filters, metrics_details=metrics_details)
        pods = response.body if hasattr(response, "body") else response.content

        # Parse JSON if needed
        if isinstance(pods, (bytes, str)):
            pods = json.loads(pods)

        # pods is a JSON-serializable list of pod details
        if not pods or len(pods) == 0:
            record_k8s_pod_metrics(metrics_details=metrics_details, status_code=404)
            return JSONResponse(
                content={
                    "message": (
                        f"Pod with id {pod_id} not found or is a system pod "
                        f"(namespace matches {K8S_IN_USE_NAMESPACE_REGEX})."
                    )
                },
                status_code=404,
            )

        pod_info = pods[0]  # Should only be one pod with this UID
        namespace = pod_info.get("namespace")
        name = pod_info.get("name")

        # Prevent deletion of system pods (already filtered by list_k8s_user_pods)
        core_v1 = get_k8s_core_v1_client()
        logger.info("Deleting pod %s in namespace %s", name, namespace)
        core_v1.delete_namespaced_pod(name=name, namespace=namespace)
        record_k8s_pod_metrics(metrics_details=metrics_details, status_code=200)
        return JSONResponse(
            content={"message": "Pod deletion triggered successfully"},
            status_code=200,
        )
    except ApiException as e:
        handle_k8s_exceptions(e, context_msg="Kubernetes API error while deleting pod")
    except ConfigException as e:
        handle_k8s_exceptions(
            e, context_msg="Kubernetes configuration error while deleting pod"
        )
