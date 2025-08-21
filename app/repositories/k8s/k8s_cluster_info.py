"""
Get cluster information from Kubernetes.
"""

import logging
import concurrent
import time
from fastapi.responses import JSONResponse
from kubernetes.client.exceptions import ApiException
from kubernetes import config
from kubernetes.config import ConfigException
import yaml

from app.metrics.helper import record_k8s_cluster_info_metrics
from app.repositories.k8s.k8s_common import (
    get_k8s_apps_v1_client,
    get_k8s_batch_v1_client,
    get_k8s_core_v1_client,
    get_k8s_version_api_client,
)
from app.repositories.k8s.k8s_node import get_k8s_nodes
from app.utils.k8s import (
    get_daemonset_basic_info,
    get_deployment_basic_info,
    get_job_basic_info,
    get_pod_basic_info,
    get_statefulset_basic_info,
    handle_k8s_exceptions,
    to_serializable,
)

logger = logging.getLogger(__name__)


def parse_cpu(cpu_str):
    """
    Parses CPU string like "1000m" to millicores (m).
    """
    # Parses CPU string like "448007813n" to millicores (m)
    if cpu_str.endswith("n"):
        return int(cpu_str[:-1]) / 1_000_000  # nanocores to millicores
    if cpu_str.endswith("u"):
        return int(cpu_str[:-1]) / 1_000  # microcores to millicores
    if cpu_str.endswith("m"):
        return int(cpu_str[:-1])  # already in millicores
    return int(cpu_str) * 1000  # assume cores, convert to millicores


def parse_memory(mem_str):
    """
    Parses memory string like "13459572Ki" to Mi.
    """
    # Parses memory string like "13459572Ki" to Mi
    units = {"Ki": 1 / 1024, "Mi": 1, "Gi": 1024}
    for unit, factor in units.items():
        if mem_str.endswith(unit):
            return int(mem_str[: -len(unit)]) * factor
    return int(mem_str) / (1024 * 1024)  # bytes to Mi


def get_version_info(version_v1):
    """
    Fetches and returns the Kubernetes version information.
    """
    return version_v1.get_code()


def get_nodes():
    """
    Fetches and returns the list of Kubernetes nodes.
    """
    start = time.time()
    nodes = get_k8s_nodes()
    logger.info("Fetched nodes: %s", nodes)
    end = time.time()
    logger.info("Time taken to fetch nodes: %.2f seconds", end - start)
    return nodes


def get_component_status(core_v1):
    """
    Fetches and returns the status of Kubernetes components.
    """
    components = core_v1.list_component_status().items
    component_status = []
    for comp in components:
        component_status.append(
            {
                "name": comp.metadata.name,
                "conditions": [
                    {"type": cond.type, "status": cond.status}
                    for cond in comp.conditions
                ],
            }
        )
    return component_status


def get_kube_system_pods_info(core_v1):
    """
    Fetches and returns basic information about pods in the kube-system namespace.
    """
    kube_system_pods = core_v1.list_namespaced_pod(namespace="kube-system").items

    kube_system_pods_info = []
    for pod in kube_system_pods:
        kube_system_pods_info.append(get_pod_basic_info(pod))
    return kube_system_pods_info


# This below function imolimented as the cluster ID is the UID of the kube-system namespace.
# This is a common practice in Kubernetes to uniquely identify clusters.
def get_cluster_id(core_v1):
    """
    Fetches and returns the cluster ID from the kube-system namespace.
    """
    cluster_id = core_v1.read_namespace(name="kube-system").metadata.uid
    return cluster_id


# This function implimented assuming that the cluster is created with kubeadm and
# cluster details are in kubeadm-config configmap in kube-system namespace.
def get_kubeadm_config(core_v1):
    """
    Fetches and returns the kubeadm configuration from the kube-system namespace.
    """
    config_map = core_v1.read_namespaced_config_map(
        name="kubeadm-config", namespace="kube-system"
    )
    raw_config = config_map.data.get("ClusterConfiguration", None)
    if raw_config:
        kubeadm_config = yaml.safe_load(raw_config)
    else:
        kubeadm_config = {}
    return kubeadm_config


def get_cluster_name(core_v1):
    """
    Fetches and returns the cluster name from the current kubeconfig context.
    """
    kubeadm_config = get_kubeadm_config(core_v1)
    if kubeadm_config and "clusterName" in kubeadm_config:
        return kubeadm_config["clusterName"]
    # If kubeadm config is not available, fallback to kubeconfig context
    config.load_incluster_config()
    contexts, active_context = config.list_kube_config_contexts()
    logger.info("Contexts: %s", contexts)
    logger.info("Active context: %s", active_context)
    cluster_name = active_context["context"]["cluster"]
    return cluster_name


def get_namespaces(core_v1):
    """
    Fetches and returns the list of namespaces in the Kubernetes cluster.
    """
    namespaces = [ns.metadata.name for ns in core_v1.list_namespace().items]
    return namespaces


def get_resources_for_namespace(
    core_v1, apps_v1, batch_v1, ns=None, resource_types=None
):
    """
    Fetches and returns basic information about specified resources in
    a specific namespace, in parallel.
    If ns is None or empty, fetches resources from all namespaces.
    resource_types: list of resource names to fetch (e.g., ["pods", "deployments"])
    """
    if resource_types is None:
        resource_types = ["pods", "deployments", "jobs", "statefulsets", "daemonsets"]

    start = time.time()
    if not ns:
        fetchers = {
            "pods": lambda: list(
                concurrent.futures.ThreadPoolExecutor().map(
                    get_pod_basic_info,
                    core_v1.list_pod_for_all_namespaces(watch=False).items,
                )
            ),
            "deployments": lambda: list(
                concurrent.futures.ThreadPoolExecutor().map(
                    get_deployment_basic_info,
                    apps_v1.list_deployment_for_all_namespaces(watch=False).items,
                )
            ),
            "jobs": lambda: list(
                concurrent.futures.ThreadPoolExecutor().map(
                    get_job_basic_info,
                    batch_v1.list_job_for_all_namespaces(watch=False).items,
                )
            ),
            "statefulsets": lambda: list(
                concurrent.futures.ThreadPoolExecutor().map(
                    get_statefulset_basic_info,
                    apps_v1.list_stateful_set_for_all_namespaces(watch=False).items,
                )
            ),
            "daemonsets": lambda: list(
                concurrent.futures.ThreadPoolExecutor().map(
                    get_daemonset_basic_info,
                    apps_v1.list_daemon_set_for_all_namespaces(watch=False).items,
                )
            ),
        }
    else:
        fetchers = {
            "pods": lambda: list(
                concurrent.futures.ThreadPoolExecutor().map(
                    get_pod_basic_info, core_v1.list_namespaced_pod(namespace=ns).items
                )
            ),
            "deployments": lambda: list(
                concurrent.futures.ThreadPoolExecutor().map(
                    get_deployment_basic_info,
                    apps_v1.list_namespaced_deployment(namespace=ns).items,
                )
            ),
            "jobs": lambda: list(
                concurrent.futures.ThreadPoolExecutor().map(
                    get_job_basic_info, batch_v1.list_namespaced_job(namespace=ns).items
                )
            ),
            "statefulsets": lambda: list(
                concurrent.futures.ThreadPoolExecutor().map(
                    get_statefulset_basic_info,
                    apps_v1.list_namespaced_stateful_set(namespace=ns).items,
                )
            ),
            "daemonsets": lambda: list(
                concurrent.futures.ThreadPoolExecutor().map(
                    get_daemonset_basic_info,
                    apps_v1.list_namespaced_daemon_set(namespace=ns).items,
                )
            ),
        }

    selected_fetchers = {k: v for k, v in fetchers.items() if k in resource_types}

    results = {}
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {
            key: executor.submit(fetcher) for key, fetcher in selected_fetchers.items()
        }
        for key, future in futures.items():
            results[key] = future.result()
    if ns is None:
        logger.info("Fetched resources for all namespaces: %s", results)
    else:
        logger.info("Fetched resources for namespace %s: %s", ns, results)
    end = time.time()
    logger.info("Total time taken to fetch resources: %.2f seconds", end - start)
    return results


def get_all_resources(core_v1, apps_v1, batch_v1, resource_types=None):
    """
    Fetches and returns basic information about specified resources in all namespaces.
    resource_types: list of resource names to fetch (e.g., ["pods", "deployments"])
    """
    if resource_types is None:
        resource_types = ["pods", "deployments", "jobs", "statefulsets", "daemonsets"]

    # Directly call get_resources_for_namespace for all namespaces (ns=None)
    ns_resources = get_resources_for_namespace(
        core_v1, apps_v1, batch_v1, ns=None, resource_types=resource_types
    )

    if ns_resources is None:
        ns_resources = {}

    # Ensure all expected keys are present and values are lists
    all_resources = {}
    for key in resource_types:
        all_resources[key] = ns_resources.get(key, [])

    logger.info("Fetched all resources: %s", all_resources)
    # Return the dictionary containing all resources
    return all_resources


def get_basic_cluster_info(core_v1, apps_v1, batch_v1):
    """
    Fetches only cluster_id, cluster_name, nodes, and pods.
    """
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {
            "cluster_id": executor.submit(get_cluster_id, core_v1),
            "cluster_name": executor.submit(get_cluster_name, core_v1),
            "nodes": executor.submit(get_nodes),
            "resources": executor.submit(
                get_all_resources, core_v1, apps_v1, batch_v1, resource_types=["pods"]
            ),
        }
        results = {key: future.result() for key, future in futures.items()}
    return {
        "cluster_id": results["cluster_id"],
        "cluster_name": results["cluster_name"],
        "nodes": results["nodes"],
        "pods": results["resources"]["pods"],
    }


def get_advanced_cluster_info(core_v1, version_v1, apps_v1, batch_v1, namespaces):
    """
    Fetches advanced cluster info (version, components, kube-system
    pods, deployments, jobs, statefulsets, daemonsets, namespaces).
    """
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {
            "version": executor.submit(get_version_info, version_v1),
            "components": executor.submit(get_component_status, core_v1),
            "kube_system_pods": executor.submit(get_kube_system_pods_info, core_v1),
            "resources": executor.submit(
                get_all_resources,
                core_v1,
                apps_v1,
                batch_v1,
                resource_types=["deployments", "jobs", "statefulsets", "daemonsets"],
            ),
        }
        results = {key: future.result() for key, future in futures.items()}
    resources = results["resources"]
    return {
        "kubernetes_version": getattr(results["version"], "git_version", None),
        "components": results["components"],
        "kube_system_pods": results["kube_system_pods"],
        "deployments": resources["deployments"],
        "jobs": resources["jobs"],
        "statefulsets": resources["statefulsets"],
        "daemonsets": resources["daemonsets"],
        "namespaces": namespaces,
    }


# Suppress R1710: All exception handlers call a function that always raises, so no return needed.
# pylint: disable=R1710
def get_cluster_info(
    advanced: bool = False, metrics_details: dict = None
) -> JSONResponse:
    """
    Fetches and returns basic or advanced information about the Kubernetes cluster.
    """
    try:
        core_v1 = get_k8s_core_v1_client()
        apps_v1 = get_k8s_apps_v1_client()
        batch_v1 = get_k8s_batch_v1_client()
        namespaces = get_namespaces(core_v1)

        # Always get basic info
        basic_info = get_basic_cluster_info(core_v1, apps_v1, batch_v1)
        cluster_resource_utilization = summarize_cluster_resource_utilization(
            basic_info
        )
        basic_info.update(cluster_resource_utilization)

        if not advanced:
            logger.info("Fetched basic cluster information")
            return basic_info

        # Advanced info
        version_v1 = get_k8s_version_api_client()
        advanced_info = get_advanced_cluster_info(
            core_v1, version_v1, apps_v1, batch_v1, namespaces
        )
        cluster_info = {**basic_info, **advanced_info}
        logger.info("Fetched advanced cluster information")
        record_k8s_cluster_info_metrics(
            metrics_details=metrics_details,
            status_code=200,
        )
        return JSONResponse(content=to_serializable(cluster_info))
    except ApiException as e:
        handle_k8s_exceptions(
            e,
            context_msg="Kubernetes API error while fetching cluster information",
            metrics_details=metrics_details,
        )
    except ConfigException as e:
        handle_k8s_exceptions(
            e,
            context_msg="Kubernetes configuration error while fetching cluster information",
            metrics_details=metrics_details,
        )
    except ValueError as e:
        handle_k8s_exceptions(
            e,
            context_msg="Value error while fetching cluster information",
            metrics_details=metrics_details,
        )


def summarize_cluster_resource_utilization(cluster_info: dict) -> dict:
    """
    Summarizes cluster resource usage and utilization statistics for UI display.

    Args:
        cluster_info (dict): Cluster information dictionary.

    Returns:
        dict: Summary of cluster resource utilization.
    """

    # loop the nodes of the cluster , get each node usage, and calculate the cluster usage""
    cluster_cpu_usage = 0
    cluster_memory_usage = 0
    cluster_cpu_availability = 0
    cluster_memory_availability = 0

    for node in cluster_info.get("nodes", []):
        node_usage = node.get("usage", {})
        cpu_str = node_usage.get("cpu", "0")
        mem_str = node_usage.get("memory", "0")
        cluster_cpu_usage += parse_cpu(cpu_str)
        cluster_memory_usage += parse_memory(mem_str)
        node_allocatable = node.get("allocatable", {})
        cluster_cpu_availability += parse_cpu(node_allocatable.get("cpu", "0"))
        cluster_memory_availability += parse_memory(node_allocatable.get("memory", "0"))

    # calculate cpu and memory utilization
    cluster_cpu_usage = round(cluster_cpu_usage, 2)  # in millicores
    cluster_memory_usage = round(cluster_memory_usage, 2)  # in Mi
    cluster_cpu_availability = round(cluster_cpu_availability, 2)  # in millicores
    cluster_memory_availability = round(cluster_memory_availability, 2)  # in Mi
    if cluster_cpu_availability > 0:
        cluster_cpu_utilization = round(
            (cluster_cpu_usage / cluster_cpu_availability) * 100, 2
        )
    else:
        cluster_cpu_utilization = 0.0
    if cluster_memory_availability > 0:
        cluster_memory_utilization = round(
            (cluster_memory_usage / cluster_memory_availability) * 100, 2
        )
    else:
        cluster_memory_utilization = 0.0

    cluster_resource_utilization = {
        "cluster_cpu_usage": cluster_cpu_usage,
        "cluster_memory_usage": cluster_memory_usage,
        "cluster_cpu_availability": cluster_cpu_availability,
        "cluster_memory_availability": cluster_memory_availability,
        "cluster_cpu_utilization": cluster_cpu_utilization,
        "cluster_memory_utilization": cluster_memory_utilization,
    }
    logger.info("Cluster resource utilization: %s", cluster_resource_utilization)

    return cluster_resource_utilization
