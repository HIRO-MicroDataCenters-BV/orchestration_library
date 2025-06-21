"""
Get cluster information from Kubernetes.
"""

import logging
import concurrent
from kubernetes.client.exceptions import ApiException
from kubernetes import config
import yaml

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
)

logger = logging.getLogger(__name__)


def get_version_info(version_v1):
    """
    Fetches and returns the Kubernetes version information.
    """
    return version_v1.get_code()


def get_nodes():
    """
    Fetches and returns the list of Kubernetes nodes.
    """
    try:
        nodes = get_k8s_nodes()
        logger.info("Fetched %s", nodes)
    except ApiException as e:
        nodes = []
        logger.error("Error fetching nodes: %s", {e})
    return nodes


def get_component_status(core_v1):
    """
    Fetches and returns the status of Kubernetes components.
    """
    try:
        components = core_v1.list_component_status().items
    except ApiException as e:
        components = []
        logger.error("Error fetching components: %s", {e})

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
    try:
        kube_system_pods = core_v1.list_namespaced_pod(namespace="kube-system").items
    except ApiException as e:
        kube_system_pods = []
        logger.error("Error fetching kube-system pods: %s", {e})

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
    try:
        cluster_id = core_v1.read_namespace(name="kube-system").metadata.uid
    except ApiException as e:
        cluster_id = None
        logger.error("Error fetching cluster ID: %s", {e})
    return cluster_id


# This function implimented assuming that the cluster is created with kubeadm and
# cluster details are in kubeadm-config configmap in kube-system namespace.
def get_kubeadm_config(core_v1):
    """
    Fetches and returns the kubeadm configuration from the kube-system namespace.
    """
    try:
        config_map = core_v1.read_namespaced_config_map(
            name="kubeadm-config", namespace="kube-system"
        )
        raw_config = config_map.data.get("ClusterConfiguration", None)
        if raw_config:
            kubeadm_config = yaml.safe_load(raw_config)
        else:
            kubeadm_config = {}
    except ApiException as e:
        kubeadm_config = {}
        logger.error("Error fetching kubeadm config: %s", {e})
    return kubeadm_config


def get_cluster_name(core_v1):
    """
    Fetches and returns the cluster name from the current kubeconfig context.
    """
    try:
        kubeadm_config = get_kubeadm_config(core_v1)
        if kubeadm_config and "clusterName" in kubeadm_config:
            return kubeadm_config["clusterName"]
        # If kubeadm config is not available, fallback to kubeconfig context
        config.load_incluster_config()
        contexts, active_context = config.list_kube_config_contexts()
        logger.info("Contexts: %s", contexts)
        logger.info("Active context: %s", active_context)
        cluster_name = active_context["context"]["cluster"]
    except config.ConfigException as e:
        cluster_name = None
        logger.error("Error fetching cluster name: %s", {e})
    return cluster_name


def get_namespaces(core_v1):
    """
    Fetches and returns the list of namespaces in the Kubernetes cluster.
    """
    try:
        namespaces = [ns.metadata.name for ns in core_v1.list_namespace().items]
    except ApiException as e:
        namespaces = []
        logger.error("Error fetching namespaces: %s", {e})
    return namespaces


def get_resources_for_namespace(core_v1, apps_v1, batch_v1, ns):
    """
    Fetches and returns basic information about resources in a specific namespace, in parallel.
    """
    def fetch_pods():
        return [
            get_pod_basic_info(pod)
            for pod in core_v1.list_namespaced_pod(namespace=ns).items
        ]

    def fetch_deployments():
        return [
            get_deployment_basic_info(dep)
            for dep in apps_v1.list_namespaced_deployment(namespace=ns).items
        ]

    def fetch_jobs():
        return [
            get_job_basic_info(job)
            for job in batch_v1.list_namespaced_job(namespace=ns).items
        ]

    def fetch_statefulsets():
        return [
            get_statefulset_basic_info(sts)
            for sts in apps_v1.list_namespaced_stateful_set(namespace=ns).items
        ]

    def fetch_daemonsets():
        return [
            get_daemonset_basic_info(ds)
            for ds in apps_v1.list_namespaced_daemon_set(namespace=ns).items
        ]

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {
            "pods": executor.submit(fetch_pods),
            "deployments": executor.submit(fetch_deployments),
            "jobs": executor.submit(fetch_jobs),
            "statefulsets": executor.submit(fetch_statefulsets),
            "daemonsets": executor.submit(fetch_daemonsets),
        }
        results = {key: future.result() for key, future in futures.items()}

    return results


def get_all_resources(core_v1, apps_v1, batch_v1, namespaces):
    """
    Fetches and returns basic information about all resources in all namespaces.
    """
    all_resources = {
        "pods": [],
        "deployments": [],
        "jobs": [],
        "statefulsets": [],
        "daemonsets": [],
    }

    def fetch_ns_resources(ns):
        return get_resources_for_namespace(core_v1, apps_v1, batch_v1, ns)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(fetch_ns_resources, namespaces))

    for ns_resources in results:
        for key in all_resources:
            all_resources[key] += ns_resources.get(key, [])

    return all_resources


def get_cluster_info():
    """
    Fetches and returns basic information about the Kubernetes cluster.
    """
    core_v1 = get_k8s_core_v1_client()
    version_v1 = get_k8s_version_api_client()
    apps_v1 = get_k8s_apps_v1_client()
    batch_v1 = get_k8s_batch_v1_client()

    namespaces = get_namespaces(core_v1)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {
            "resources": executor.submit(get_all_resources, core_v1, apps_v1, batch_v1, namespaces),
            "version": executor.submit(get_version_info, version_v1),
            "components": executor.submit(get_component_status, core_v1),
            "kube_system_pods": executor.submit(get_kube_system_pods_info, core_v1),
            "cluster_id": executor.submit(get_cluster_id, core_v1),
            "cluster_name": executor.submit(get_cluster_name, core_v1),
            "nodes": executor.submit(get_nodes),
        }

        results = {key: future.result() for key, future in futures.items()}

    resources = results["resources"]
    cluster_info = {
        "kubernetes_version": getattr(results["version"], "git_version", None),
        "components": results["components"],
        "kube_system_pods": results["kube_system_pods"],
        "cluster_id": results["cluster_id"],
        "cluster_name": results["cluster_name"],
        "nodes": results["nodes"],
        "namespaces": namespaces,
        "pods": resources["pods"],
        "deployments": resources["deployments"],
        "jobs": resources["jobs"],
        "statefulsets": resources["statefulsets"],
        "daemonsets": resources["daemonsets"],
    }

    return cluster_info
