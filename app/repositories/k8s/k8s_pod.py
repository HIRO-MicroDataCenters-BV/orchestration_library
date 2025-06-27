"""
List the pods in the Kubernetes cluster.
"""

import re
from fastapi.responses import JSONResponse
from kubernetes.client.rest import ApiException
from kubernetes import config
from app.utils.exceptions import handle_k8s_exceptions
from app.utils.k8s import get_pod_details
from app.repositories.k8s.k8s_common import (
    K8S_IN_USE_NAMESPACE_REGEX,
    get_k8s_core_v1_client,
)


def list_k8s_pods(
    namespace=None, name=None, pod_id=None, status=None, exclude_namespace_regex=None
) -> JSONResponse:
    """
    List all pods in the specified namespace.
    If no namespace is specified, list all pods in all namespaces.
    """
    try:
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
    except ApiException as e:
        handle_k8s_exceptions(e, context_msg="Kubernetes API error while listing pods")
    except config.ConfigException as e:
        handle_k8s_exceptions(
            e, context_msg="Kubernetes configuration error while listing pods"
        )
    except ValueError as e:
        handle_k8s_exceptions(e, context_msg="Value error while listing pods")


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
