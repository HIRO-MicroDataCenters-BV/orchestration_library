"""
List the pods in the Kubernetes cluster.
"""

from enum import Enum
import json
import logging
import re
import time
from fastapi.responses import JSONResponse

from httpx import Response
from kubernetes import client as k8s_client
from kubernetes.client.rest import ApiException
from kubernetes.config import ConfigException
from kubernetes.client import V1Pod

from app.metrics.helper import record_k8s_pod_metrics
from app.utils.helper import send_http_request
from app.utils.k8s import get_pod_details, handle_k8s_exceptions
from app.repositories.k8s.k8s_common import (
    get_k8s_apps_v1_client,
    get_k8s_core_v1_client,
)
from app.utils.constants import K8S_IN_USE_NAMESPACE_REGEX


logger = logging.getLogger(__name__)


class ScaleType(str, Enum):
    """
    Enum for scaling types: UP or DOWN.
    """

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


def get_k8s_pod_obj(pod_id=None, pod_name=None, namespace=None) -> V1Pod:
    """
    Return full Kubernetes Pod spec (raw API object) using pod UID or name.
    Kubernetes API does not support direct lookup by UID, so we iterate all pods.
    """
    if pod_id is None and pod_name is None:
        raise ValueError("Either pod_id or pod_name must be provided")
    core_v1 = get_k8s_core_v1_client()
    all_pods = core_v1.list_pod_for_all_namespaces(watch=False)
    for pod in all_pods.items:
        if (pod_id and pod.metadata.uid == str(pod_id)) or (
            pod_name and pod.metadata.name == str(pod_name)
        ):
            if namespace is None or pod.metadata.namespace == str(namespace):
                return pod
    return None


def get_k8s_pod_containrers_resources(pod: V1Pod):
    """
    Extract resource requests and limits for all containers in the pod.
    Returns a list of dicts with container name, requests, and limits.
    """
    containers_info = []
    for container in pod.spec.containers:
        resources = container.resources
        requests = resources.requests if resources and resources.requests else {}
        limits = resources.limits if resources and resources.limits else {}
        containers_info.append(
            {
                "name": container.name,
                "requests": requests,
                "limits": limits,
            }
        )
    return containers_info


def get_managed_controller(pod):
    """
    Check if the pod is owned by a higher-level controller
    (ReplicaSet, StatefulSet, etc.).
    """
    owners = getattr(pod.metadata, "owner_references", None)
    if not owners:
        return None
    for owner in owners:
        # owner.controller may be None; treat truthy as controller-managed
        if getattr(owner, "controller", False):
            return owner
    return None


def get_pod_and_controller(pod_id=None, pod_name=None, namespace=None):
    """
    Fetch pod spec and its managing controller owner (if any).
    """
    pod_spec = get_k8s_pod_obj(pod_id, pod_name, namespace)
    if not pod_spec:
        return None, None
    controller_owner = get_managed_controller(pod_spec)
    return pod_spec, controller_owner


def sanitize_naked_pod_for_recreation(pod):
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


def wait_for_pod_deletion(
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
        pod_spec, controller_owner = get_pod_and_controller(pod_id)
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

        logger.info(
            "Recreating pod %s (UID=%s) in namespace %s; controller_owner=%s",
            name,
            pod_id,
            namespace,
            controller_owner,
        )

        # Delete the existing pod
        core_v1.delete_namespaced_pod(name=name, namespace=namespace)

        if controller_owner:
            logger.info(
                "Pod %s (UID=%s) is controller-owned; relying on controller to recreate it.",
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
        recreated_body = sanitize_naked_pod_for_recreation(pod_spec)
        # Naked pod: wait for deletion completion
        deleted = wait_for_pod_deletion(name, namespace)
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


def resolve_controller(apps_v1, controller_owner, namespace):
    """
    Determine controller type, name, and current replicas.
    """
    if controller_owner.kind == "ReplicaSet":
        replica_set = apps_v1.read_namespaced_replica_set(
            controller_owner.name, namespace
        )
        rs_owners = getattr(replica_set.metadata, "owner_references", None)
        if not rs_owners:
            return replica_set.spec.replicas, "ReplicaSet", controller_owner.name
        for owner in rs_owners:
            if owner.kind == "Deployment":
                deployment = apps_v1.read_namespaced_deployment(owner.name, namespace)
                return deployment.spec.replicas, "Deployment", owner.name
    if controller_owner.kind == "StatefulSet":
        stateful_set = apps_v1.read_namespaced_stateful_set(
            controller_owner.name, namespace
        )
        return stateful_set.spec.replicas, "StatefulSet", controller_owner.name
    raise ValueError(
        f"Unsupported controller kind '{controller_owner.kind}' for scaling."
    )


def calculate_target_replicas(
    current: int, scale_type: ScaleType, scale_delta: int
) -> int:
    """
    Compute target replica count based on scale_type.
    """
    if scale_type == ScaleType.UP:
        return current + scale_delta
    return max(current - scale_delta, 0)


def patch_scale(
    apps_v1, controller_kind: str, controller_name: str, namespace: str, replicas: int
):
    """
    Apply scale change to the appropriate controller.
    """
    body = {"spec": {"replicas": replicas}}
    if controller_kind == "Deployment":
        apps_v1.patch_namespaced_deployment_scale(controller_name, namespace, body)
    elif controller_kind == "ReplicaSet":
        apps_v1.patch_namespaced_replica_set_scale(controller_name, namespace, body)
    elif controller_kind == "StatefulSet":
        apps_v1.patch_namespaced_stateful_set_scale(controller_name, namespace, body)
    else:
        raise ValueError(
            f"Cannot patch scale for unsupported controller kind '{controller_kind}'."
        )


def scale_k8s_user_pod(
    pod_id, scale_type: ScaleType, scale_delta=1, metrics_details=None
) -> JSONResponse:
    """
    Orchestrate scaling of a pod's managing controller.
    """
    try:
        pod_spec, controller_owner = get_pod_and_controller(pod_id)
        if not pod_spec:
            record_k8s_pod_metrics(metrics_details=metrics_details, status_code=404)
            return JSONResponse(
                content={"message": f"Pod with id {pod_id} not found."},
                status_code=404,
            )
        if not controller_owner:
            record_k8s_pod_metrics(metrics_details=metrics_details, status_code=400)
            return JSONResponse(
                content={
                    "message": (
                        "Pod is not managed by any controller like Deployment, "
                        "StatefulSet, or ReplicaSet. Cannot scale."
                    )
                },
                status_code=400,
            )
        namespace = pod_spec.metadata.namespace
        apps_v1 = get_k8s_apps_v1_client()

        current_replicas, controller_kind, controller_name = resolve_controller(
            apps_v1, controller_owner, namespace
        )
        target_replicas = calculate_target_replicas(
            current_replicas, scale_type, scale_delta
        )
        patch_scale(
            apps_v1, controller_kind, controller_name, namespace, target_replicas
        )

        record_k8s_pod_metrics(metrics_details=metrics_details, status_code=200)
        return JSONResponse(
            content={
                "message": (
                    f"Scaled {controller_kind} '{controller_name}' to {target_replicas} replicas."
                ),
                "pod_id": str(pod_id),
                "namespace": namespace,
                "controller_kind": controller_kind,
                "controller_name": controller_name,
                "previous_replicas": current_replicas,
                "replicas": target_replicas,
                "scale_type": scale_type.value,
                "scale_delta": scale_delta,
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


def redeploy_pod_via_alert_action_service(
    pod_name: str, namespace: str, service_url: str
) -> Response:
    """
    Trigger pod redeploy via an external alert action service.
    Args:
        pod_name (str): The name of the pod to redeploy.
        namespace (str): The namespace of the pod.
        service_url (str): The URL of the alert action service.
    Returns:
        Response: The HTTP response from the alert action service.
    """

    logger.info(
        "Triggering pod redeploy via alert action service: "
        "pod_name=%s, namespace=%s, service_url=%s",
        pod_name,
        namespace,
        service_url,
    )
    request_data = {
        "method": "action.Redeploy",
        "params": [
            {
                "pod": {"namespace": namespace, "name": pod_name}
            }
        ],
        "id": "1",
    }

    # curl -X POST -H "Content-Type: application/json" \
#   -d "{\"method\":\"action.Redeploy\",\"params\":[{\"pod\": {\"namespace\": \"ul\", \"name\": \"$pod_to_redeploy\"}}], \"id\":\"1\"}" \
#   http://localhost:3030/rpc

    return send_http_request(
        method="POST",
        url=f"{service_url}",
        data=json.dumps(request_data),
        headers={"Content-Type": "application/json"},
    )


def delete_pod_via_alert_action_service(
    pod_name: str, namespace: str, node_name: str, service_url: str
) -> Response:
    """
    Trigger pod deletion via an external alert action service.
    Args:
        pod_name (str): The name of the pod to delete.
        namespace (str): The namespace of the pod.
        node_name (str): The name of the node where the pod is running.
        service_url (str): The URL of the alert action service.
    Returns:
        Response: The HTTP response from the alert action service.
    """

    logger.info(
        "Triggering pod deletion via alert action service: "
        "pod_name=%s, namespace=%s, node_name=%s, service_url=%s",
        pod_name,
        namespace,
        node_name,
        service_url,
    )
    request_data = {
        "method": "action.Delete",
        "params": [
            {
                "pod": {"namespace": namespace, "name": pod_name},
                "node": {"name": node_name},
            }
        ],
        "id": "1",
    }

    return send_http_request(
        method="POST",
        url=f"{service_url}",
        data=json.dumps(request_data),
        headers={"Content-Type": "application/json"},
    )


def scaleup_pod_via_alert_action_service(
    pod_name: str, namespace: str, node_name: str, service_url: str
) -> Response:
    """
    Trigger pod scale-up via an external alert action service.
    Args:
        pod_name (str): The name of the pod to scale up.
        namespace (str): The namespace of the pod.
        node_name (str): The name of the node where the pod is running.
        service_url (str): The URL of the alert action service.
    Returns:
        Response: The HTTP response from the alert action service.
    """

    logger.info(
        "Triggering pod scale-up via alert action service: "
        "pod_name=%s, namespace=%s, node_name=%s, service_url=%s",
        pod_name,
        namespace,
        node_name,
        service_url,
    )
    pod_spec, controller_owner = get_pod_and_controller(
        pod_name=pod_name, namespace=namespace
    )
    if not pod_spec:
        logger.error("Pod %s in namespace %s not found.", pod_name, namespace)
        return None
    if not controller_owner:
        logger.error(
            "Pod %s in namespace %s is not controller-owned; cannot scale up.",
            pod_name,
            namespace,
        )
        return None
    apps_v1 = get_k8s_apps_v1_client()
    current_replicas, controller_kind, controller_name = resolve_controller(
        apps_v1, controller_owner, namespace
    )
    # This will scale the deployment to 1.
    # Example:
    # curl -X POST \
    #   -H "Content-Type: application/json" \
    #   -d '{
    #         "method": "action.Scale",
    #         "params": [
    #             {
    #                 "workload": {
    #                     "namespace": "ul",
    #                     "kind": "Deployment",
    #                     "name": "pending-test"
    #                 },
    #                 "replicas": 1
    #             }
    #         ],
    #         "id": "1"
    #       }'
    request_data = {
        "method": "action.Scale",
        "params": [
            {
                "workload": {
                    "namespace": namespace,
                    "name": controller_name,
                    "kind": controller_kind,
                },
                "replicas": current_replicas + 1,
            }
        ],
        "id": "1",
    }

    return send_http_request(
        method="POST",
        url=f"{service_url}",
        data=json.dumps(request_data),
        headers={"Content-Type": "application/json"},
    )


def get_updated_container_resources(
    container: dict, update_resource_type: str, percent_increase: float = 0.2
):
    """
    Calculate updated resource requests and limits for a container.
    Args:
        container (dict): Container resource specifications.
            container_name (str): Name of the container.
            requests (dict): Current resource requests for the container.
            limits (dict): Current resource limits for the container.
        update_resource_type (str): Type of resource to update ("cpu" or "memory").
        percent_increase (float): Percentage increase to apply to the resource.
    Returns:
        dict: Updated requests and limits for the container.
    """
    current_requests = container.get("requests", {})
    current_limits = container.get("limits", {})
    new_requests = current_requests.copy()
    new_limits = current_limits.copy()

    if update_resource_type == "cpu":
        current_cpu_request = current_requests.get("cpu")
        current_cpu_limit = current_limits.get("cpu")
        if current_cpu_request:
            if current_cpu_request.endswith("m"):
                cpu_millicores = int(current_cpu_request[:-1])
                new_cpu_millicores = int(cpu_millicores * (1.0 + percent_increase))
                new_requests["cpu"] = f"{new_cpu_millicores}m"
            else:
                cpu_cores = float(current_cpu_request)
                new_cpu_cores = round(cpu_cores * (1.0 + percent_increase), 2)
                new_requests["cpu"] = str(new_cpu_cores)
        if current_cpu_limit:
            if current_cpu_limit.endswith("m"):
                cpu_millicores = int(current_cpu_limit[:-1])
                new_cpu_millicores = int(cpu_millicores * (1.0 + percent_increase))
                new_limits["cpu"] = f"{new_cpu_millicores}m"
            else:
                cpu_cores = float(current_cpu_limit)
                new_cpu_cores = round(cpu_cores * (1.0 + percent_increase), 2)
                new_limits["cpu"] = str(new_cpu_cores)

    return {"requests": new_requests, "limits": new_limits}


def update_pod_resources_via_alert_action_service(
    controller_details: dict,
    pod_details: dict,
    containers_resources: list,
    service_url: str,
    update_resource_type: str = "cpu",
):
    """
    Trigger pod resource update via an external alert action service.
    Args:
        controller_details (dict): Details of the managing controller.
            kind (str): Kind of the controller (e.g., Deployment, StatefulSet).
            name (str): Name of the controller.
            replicas (int): Number of replicas managed by the controller.
        pod_details (dict): Details of the pod.
            namespace (str): Namespace of the pod.
            name (str): Name of the pod.
        containers_resources (list): List of container resource specifications.
            container_name (str): Name of the container.
            requests (dict): Resource requests for the container.
            limits (dict): Resource limits for the container.
        service_url (str): The URL of the alert action service.
        update_resource_type (str): Type of resource to update ("cpu" or "memory").
    Returns:
        bool: True if update was successful, False otherwise.
    """

    for container in containers_resources:
        if container.get("requests") is None and container.get("limits") is None:
            logger.error(
                "Container %s is missing requests and limits; cannot update resources.",
                container.get("name"),
            )
            continue
        updated_resources = get_updated_container_resources(
            container, update_resource_type
        )
        request_data = {
            "method": "action.UpdateResources",
            "params": [
                {
                    "workload": {
                        "namespace": pod_details.get("namespace"),
                        "kind": controller_details.get("kind"),
                        "name": controller_details.get("name"),
                    },
                    "resources": {
                        "container_name": container.get("name"),
                        "cpu_request": updated_resources["requests"].get("cpu"),
                        "cpu_limit": updated_resources["limits"].get("cpu"),
                        "memory_request": updated_resources["requests"].get("memory"),
                        "memory_limit": updated_resources["limits"].get("memory"),
                    },
                }
            ],
            "id": "1",
        }

        send_http_request(
            method="POST",
            url=f"{service_url}",
            data=json.dumps(request_data),
            headers={"Content-Type": "application/json"},
        )
