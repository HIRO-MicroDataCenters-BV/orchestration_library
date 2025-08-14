"""
Get the parent controller of a Kubernetes pod.
"""

import logging
from fastapi.responses import JSONResponse
from kubernetes.client.rest import ApiException
from kubernetes.config import ConfigException
from app.metrics.helper import record_k8s_pod_parent_metrics
from app.repositories.k8s.k8s_common import (
    get_k8s_apps_v1_client,
    get_k8s_batch_v1_client,
    get_k8s_core_v1_client,
)
from app.utils.exceptions import K8sValueError
from app.utils.k8s import handle_k8s_exceptions


logger = logging.getLogger(__name__)


def get_pod_by_name_or_uid(core_v1, namespace, pod_name=None, pod_id=None):
    """
    Get a pod by its name or UID.
    """
    if not pod_name and not pod_id:
        raise K8sValueError("Either pod_name or pod_id must be provided.")

    if pod_name:
        return core_v1.read_namespaced_pod(name=pod_name, namespace=namespace)

    pod_list = core_v1.list_namespaced_pod(namespace=namespace)
    for pod in pod_list.items:
        if pod.metadata.uid == pod_id:
            return pod
    logger.warning(
        "Pod with UID %s not found in namespace %s. Ensure the pod exists and the UID is correct.",
        pod_id,
        namespace,
    )

    return None


def get_deployment_from_replicaset(apps_v1, replicaset_name, namespace):
    """
    Get the deployment from a replicaset.
    """
    rs = apps_v1.read_namespaced_replica_set(name=replicaset_name, namespace=namespace)
    for rs_owner in rs.metadata.owner_references or []:
        if rs_owner.kind == "Deployment":
            deployment = apps_v1.read_namespaced_deployment(
                name=rs_owner.name, namespace=namespace
            )
            return {
                "name": deployment.metadata.name,
                "namespace": deployment.metadata.namespace,
                "api_version": deployment.api_version,
                "kind": "Deployment",
                "current_scale": deployment.spec.replicas,
            }
    logger.warning(
        "ReplicaSet %s in namespace %s has no owner of kind Deployment.",
        replicaset_name,
        namespace,
    )
    return None


def get_controller_details(apps_v1, batch_v1, namespace, owner):
    """
    Get the details of the controller (Deployment, StatefulSet, DaemonSet, or Job).
    """
    kind = owner.kind
    name = owner.name

    if kind == "ReplicaSet":
        return get_deployment_from_replicaset(apps_v1, name, namespace)

    if kind == "StatefulSet":
        ss = apps_v1.read_namespaced_stateful_set(name=name, namespace=namespace)
        return {
            "name": ss.metadata.name,
            "namespace": ss.metadata.namespace,
            "api_version": ss.api_version,
            "kind": "StatefulSet",
            "current_scale": ss.spec.replicas,
        }

    if kind == "DaemonSet":
        ds = apps_v1.read_namespaced_daemon_set(name=name, namespace=namespace)
        return {
            "name": ds.metadata.name,
            "namespace": ds.metadata.namespace,
            "api_version": ds.api_version,
            "kind": "DaemonSet",
            "current_scale": ds.status.desired_number_scheduled,
        }

    if kind == "Job":
        job = batch_v1.read_namespaced_job(name=name, namespace=namespace)
        return {
            "name": job.metadata.name,
            "namespace": job.metadata.namespace,
            "api_version": job.api_version,
            "kind": "Job",
            "current_scale": job.spec.parallelism or 1,
        }
    logger.warning(
        "Owner %s of kind %s not recognized or not supported in this context.",
        name,
        kind,
    )

    return None


# Suppress R1710: All exception handlers call a function that always raises, so no return needed.
# pylint: disable=R1710
def get_parent_controller_details_of_pod(
    namespace, pod_name=None, pod_id=None, metrics_details=None
) -> JSONResponse:
    """
    Get the parent controller of a Kubernetes pod.
    Args:
        pod_name (str): Name of the pod.
        pod_id (str): UID of the pod.
        namespace (str): Namespace of the pod.
    Returns:
        dict: Details of the parent controller (Deployment, StatefulSet, DaemonSet, or Job).
    """

    try:
        core_v1 = get_k8s_core_v1_client()
        apps_v1 = get_k8s_apps_v1_client()
        batch_v1 = get_k8s_batch_v1_client()

        pod = get_pod_by_name_or_uid(core_v1, namespace, pod_name, pod_id)
        if not pod:
            record_k8s_pod_parent_metrics(
                metrics_details=metrics_details,
                status_code=200,
            )
            return {
                "message": (
                    f"No pod found with name: {pod_name} or UID: {pod_id} "
                    f"in namespace: {namespace}"
                )
            }

        if not pod.metadata.owner_references:
            record_k8s_pod_parent_metrics(
                metrics_details=metrics_details,
                status_code=200,
            )
            return {"message": "Pod has no owner references (standalone pod)"}

        for owner in pod.metadata.owner_references:
            controller_details = get_controller_details(
                apps_v1, batch_v1, namespace, owner
            )
            if controller_details:
                record_k8s_pod_parent_metrics(
                    metrics_details=metrics_details,
                    status_code=200,
                )
                return JSONResponse(content=controller_details)
        logger.warning(
            "Pod %s in namespace %s has no recognized parent controller.",
            pod_name or pod_id,
            namespace,
        )
        return {
            "message": "No known controller found (Deployment, StatefulSet, DaemonSet, or Job)"
        }
    except ApiException as e:
        handle_k8s_exceptions(
            e,
            context_msg=(
                f"Kubernetes API error while getting parent controller of pod "
                f"{pod_name or pod_id} in namespace {namespace}"
            ),
        )
    except ConfigException as e:
        handle_k8s_exceptions(
            e,
            context_msg=(
                f"Kubernetes configuration error while getting parent controller of pod "
                f"{pod_name or pod_id} in namespace {namespace}"
            ),
        )
    except ValueError as e:
        handle_k8s_exceptions(
            e,
            context_msg=(
                f"Value error while getting parent controller of pod "
                f"{pod_name or pod_id} in namespace {namespace}"
            ),
        )
