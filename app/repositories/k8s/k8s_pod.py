"""
List the pods in the Kubernetes cluster.
"""

from enum import Enum
import json
import logging
import re
import time
from fastapi.responses import JSONResponse

from kubernetes import client as k8s_client
from kubernetes.client.rest import ApiException
from kubernetes.config import ConfigException

from app.metrics.helper import record_k8s_pod_metrics
from app.utils.k8s import get_pod_details, handle_k8s_exceptions
from app.repositories.k8s.k8s_common import (
    get_k8s_apps_v1_client,
    get_k8s_core_v1_client,
)
from app.utils.constants import K8S_IN_USE_NAMESPACE_REGEX


logger = logging.getLogger(__name__)


class ScaleType(str, Enum):
    UP = "UP"
    DOWN = "DOWN"

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


def get_k8s_user_pod_info(pod_id, metrics_details=None):
    """
    Get a pod by pod_id (UID). Will not return system pods.
    """
    pod_filters = {"pod_id": str(pod_id)}
    response = list_k8s_user_pods(
        pod_filters=pod_filters, metrics_details=metrics_details
    )
    pods = response.body

    # Parse JSON if needed
    if isinstance(pods, bytes):
        pods = json.loads(pods.decode("utf-8"))
    elif isinstance(pods, str):
        pods = json.loads(pods)

    if not pods or len(pods) == 0:
        return None
    pod_info = pods[0]  # Should only be one pod with this UID

    return pod_info


def delete_k8s_user_pod(pod_id, metrics_details=None) -> JSONResponse:
    """
    Delete a pod by pod_id (UID). Will not delete system pods.
    """
    try:
        pod_info = get_k8s_user_pod_info(pod_id, metrics_details=metrics_details)

        if not pod_info:
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


def get_k8s_pod_spec(pod_id):
    """
    Return full Kubernetes Pod spec (raw API object) using pod UID.
    Kubernetes API does not support direct lookup by UID, so we iterate all pods.
    """
    core_v1 = get_k8s_core_v1_client()
    all_pods = core_v1.list_pod_for_all_namespaces(watch=False)
    for pod in all_pods.items:
        if pod.metadata.uid == str(pod_id):
            return pod
    return None


def _get_managed_controller(pod):
    """
    Check if the pod is owned by a higher-level controller (ReplicaSet, StatefulSet, etc.).
    """
    owners = getattr(pod.metadata, "owner_references", None)
    if not owners:
        return None
    for owner in owners:
        # owner.controller may be None; treat truthy as controller-managed
        if getattr(owner, "controller", False):
            return owner
    return None


def _sanitize_naked_pod_for_recreation(pod):
    """
    Prepare a naked pod (no controller owner) for recreation.
    Remove fields that must not be resent on create.
    Returns a dict suitable for create_namespaced_pod().
    """
    pod.metadata.resource_version = None
    pod.metadata.uid = None
    pod.metadata.creation_timestamp = None
    pod.metadata.managed_fields = None
    pod.status = None

    # Optional: remove finalizers (leave if needed)
    api_client = k8s_client.ApiClient()
    return api_client.sanitize_for_serialization(pod)


def _wait_for_pod_deletion(
    name: str, namespace: str, timeout: float = 60.0, interval: float = 1.0
) -> bool:
    """
    Poll the API until the pod no longer exists (404) or timeout exceeded.
    Returns True if deleted, False if timeout.
    """
    core_v1 = get_k8s_core_v1_client()
    start = time.time()
    while time.time() - start < timeout:
        try:
            core_v1.read_namespaced_pod(name=name, namespace=namespace)
            # Pod still exists; sleep and retry
            time.sleep(interval)
        except ApiException as e:
            if e.status == 404:
                return True  # Gone
            # Other API errors: brief sleep then retry
            time.sleep(interval)
    return False


def recreate_k8s_user_pod(pod_id, metrics_details=None) -> JSONResponse:
    """
    Recreate a pod by pod_id (UID). Will not recreate system pods.
    """
    try:
        pod_spec = get_k8s_pod_spec(pod_id)
        if not pod_spec:
            record_k8s_pod_metrics(metrics_details=metrics_details, status_code=404)
            return JSONResponse(
                content={"message": f"Pod with id {pod_id} not found."},
                status_code=404,
            )

        namespace = pod_spec.metadata.namespace
        name = pod_spec.metadata.name

        core_v1 = get_k8s_core_v1_client()
        logger.info("Recreating pod %s in namespace %s", name, namespace)

        managed_controller = _get_managed_controller(pod_spec)

        logger.info(
            "Recreating pod %s (UID=%s) in namespace %s; managed_controller=%s",
            name,
            pod_id,
            namespace,
            managed_controller,
        )

        # Delete the existing pod
        core_v1.delete_namespaced_pod(name=name, namespace=namespace)

        if managed_controller:
            logger.info(
                "Pod %s (UID=%s) is controller-managed; relying on controller to recreate it.",
                name,
                pod_id,
            )
            record_k8s_pod_metrics(metrics_details=metrics_details, status_code=200)
            return JSONResponse(
                content={
                    "message": (
                        "Pod deletion triggered. Controller will create a replacement."
                    ),
                    "pod_id": str(pod_id),
                    "namespace": namespace,
                    "name": name,
                    "controller_managed": True,
                },
                status_code=200,
            )

        # Remove fields that should not be included when recreating
        pod_spec.metadata.resource_version = None
        pod_spec.metadata.uid = None
        pod_spec.status = None

        # Naked pod: we must manually recreate
        recreated_body = _sanitize_naked_pod_for_recreation(pod_spec)
        # Naked pod: wait for deletion completion
        deleted = _wait_for_pod_deletion(name, namespace)
        if not deleted:
            record_k8s_pod_metrics(metrics_details=metrics_details, status_code=409)
            return JSONResponse(
                content={
                    "message": "Timeout waiting for pod to finish deleting; recreation aborted.",
                    "pod_id": str(pod_id),
                    "namespace": namespace,
                    "name": name,
                    "controller_managed": False,
                },
                status_code=409,
            )
        core_v1.create_namespaced_pod(namespace=namespace, body=recreated_body)

        record_k8s_pod_metrics(metrics_details=metrics_details, status_code=200)
        return JSONResponse(
            content={
                "message": "Naked pod deletion + recreation triggered successfully.",
                "pod_id": str(pod_id),
                "namespace": namespace,
                "name": name,
                "controller_managed": False,
            },
            status_code=200,
        )
    except ApiException as e:
        handle_k8s_exceptions(
            e, context_msg="Kubernetes API error while recreating pod"
        )
    except ConfigException as e:
        handle_k8s_exceptions(
            e, context_msg="Kubernetes configuration error while recreating pod"
        )
    except ValueError as e:
        handle_k8s_exceptions(e, context_msg="Value error while recreating pod")


def scale_k8s_user_pod(
    pod_id, scale_type: ScaleType, scale_delta=1, metrics_details=None
) -> JSONResponse:
    """
    Scale a pod's controller (Deployment, StatefulSet) by pod_id (UID).
    scale_type: "UP" to increase by 1, "DOWN" to decrease by 1.
    Will not scale system pods.
    """
    try:
        pod_spec = get_k8s_pod_spec(pod_id)
        if not pod_spec:
            record_k8s_pod_metrics(metrics_details=metrics_details, status_code=404)
            return JSONResponse(
                content={"message": f"Pod with id {pod_id} not found."},
                status_code=404,
            )

        namespace = pod_spec.metadata.namespace

        controller_owner = _get_managed_controller(pod_spec)
        if not controller_owner:
            record_k8s_pod_metrics(metrics_details=metrics_details, status_code=400)
            return JSONResponse(
                content={"message": "Pod is not managed by any controller"},
                status_code=400,
            )

        apps_v1 = get_k8s_apps_v1_client()
        current_replicas = None
        controller_kind = None
        controller_name = None

        if controller_owner.kind == "ReplicaSet":
            replica_set = apps_v1.read_namespaced_replica_set(
                controller_owner.name, namespace
            )
            rs_owners = getattr(replica_set.metadata, "owner_references", [])
            deployment_owner = None
            for owner in rs_owners:
                if owner.kind == "Deployment":
                    deployment_owner = owner
                    break
            if not deployment_owner:
                current_replicas = replica_set.spec.replicas
                controller_kind = "ReplicaSet"
                controller_name = controller_owner.name
            else:
                deployment = apps_v1.read_namespaced_deployment(
                    deployment_owner.name, namespace
                )
                current_replicas = deployment.spec.replicas
                controller_kind = "Deployment"
                controller_name = deployment_owner.name
        elif controller_owner.kind == "StatefulSet":
            stateful_set = apps_v1.read_namespaced_stateful_set(
                controller_owner.name, namespace
            )
            current_replicas = stateful_set.spec.replicas
            controller_kind = "StatefulSet"
            controller_name = controller_owner.name
        else:
            record_k8s_pod_metrics(metrics_details=metrics_details, status_code=400)
            return JSONResponse(
                content={
                    "message": f"Scaling for controller kind '{controller_owner.kind}' is not supported."
                },
                status_code=400,
            )

        if scale_type == ScaleType.UP:
            replicas = current_replicas + scale_delta
        elif scale_type == ScaleType.DOWN:
            replicas = max(current_replicas - scale_delta, 0)
        else:
            record_k8s_pod_metrics(metrics_details=metrics_details, status_code=400)
            return JSONResponse(
                content={"message": "scale_type must be 'UP' or 'DOWN'."},
                status_code=400,
            )

        body = {"spec": {"replicas": replicas}}
        if controller_kind == "Deployment":
            apps_v1.patch_namespaced_deployment_scale(controller_name, namespace, body)
        elif controller_kind == "ReplicaSet":
            apps_v1.patch_namespaced_replica_set_scale(controller_name, namespace, body)
        elif controller_kind == "StatefulSet":
            apps_v1.patch_namespaced_stateful_set_scale(
                controller_name, namespace, body
            )

        record_k8s_pod_metrics(metrics_details=metrics_details, status_code=200)
        return JSONResponse(
            content={
                "message": f"Scaled {controller_kind} '{controller_name}' to {replicas} replicas.",
                "pod_id": str(pod_id),
                "namespace": namespace,
                "controller_kind": controller_kind,
                "controller_name": controller_name,
                "replicas": replicas,
            },
            status_code=200,
        )
    except ApiException as e:
        handle_k8s_exceptions(
            e, context_msg="Kubernetes API error while scaling pod controller"
        )
    except ConfigException as e:
        handle_k8s_exceptions(
            e, context_msg="Kubernetes configuration error while scaling pod controller"
        )
    except ValueError as e:
        handle_k8s_exceptions(e, context_msg="Value error while scaling pod controller")
