"""
Get cluster information from Kubernetes.
"""

from kubernetes.client.exceptions import ApiException
from kubernetes import config

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
        print(f"Fetched {nodes}")
    except ApiException as e:
        nodes = []
        print(f"Error fetching nodes: {e}")
    return nodes


def get_component_status(core_v1):
    """
    Fetches and returns the status of Kubernetes components.
    """
    try:
        components = core_v1.list_component_status().items
    except ApiException as e:
        components = []
        print(f"Error fetching components: {e}")

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
        print(f"Error fetching kube-system pods: {e}")

    kube_system_pods_info = []
    for pod in kube_system_pods:
        kube_system_pods_info.append(get_pod_basic_info(pod))
    return kube_system_pods_info


def get_cluster_id(core_v1):
    """
    Fetches and returns the cluster ID from the kube-system namespace.
    """
    try:
        cluster_id = core_v1.read_namespace(name="kube-system").metadata.uid
    except ApiException as e:
        cluster_id = None
        print(f"Error fetching cluster ID: {e}")
    return cluster_id


def get_cluster_name():
    """
    Fetches and returns the cluster name from the current kubeconfig context.
    """
    try:
        config.load_incluster_config()
        contexts, active_context = config.list_kube_config_contexts()
        print(f"Contexts: {contexts}")
        print(f"Active context: {active_context}")
        cluster_name = active_context["context"]["cluster"]
    except config.ConfigException as e:
        cluster_name = None
        print(f"Error fetching cluster name: {e}")
    return cluster_name


def get_namespaces(core_v1):
    """
    Fetches and returns the list of namespaces in the Kubernetes cluster.
    """
    try:
        namespaces = [ns.metadata.name for ns in core_v1.list_namespace().items]
    except ApiException as e:
        namespaces = []
        print(f"Error fetching namespaces: {e}")
    return namespaces


def get_resources_for_namespace(core_v1, apps_v1, batch_v1, ns):
    """
    Fetches and returns basic information about resources in a specific namespace.
    """
    pods = [
        get_pod_basic_info(pod)
        for pod in core_v1.list_namespaced_pod(namespace=ns).items
    ]
    deployments = [
        get_deployment_basic_info(dep)
        for dep in apps_v1.list_namespaced_deployment(namespace=ns).items
    ]
    jobs = [
        get_job_basic_info(job)
        for job in batch_v1.list_namespaced_job(namespace=ns).items
    ]
    statefulsets = [
        get_statefulset_basic_info(sts)
        for sts in apps_v1.list_namespaced_stateful_set(namespace=ns).items
    ]
    daemonsets = [
        get_daemonset_basic_info(ds)
        for ds in apps_v1.list_namespaced_daemon_set(namespace=ns).items
    ]
    return pods, deployments, jobs, statefulsets, daemonsets


def get_all_resources(core_v1, apps_v1, batch_v1, namespaces):
    """
    Fetches and returns basic information about all resources in all namespaces.
    """
    pods = []
    deployments = []
    jobs = []
    statefulsets = []
    daemonsets = []
    for ns in namespaces:
        ns_pods, ns_deployments, ns_jobs, ns_statefulsets, ns_daemonsets = (
            get_resources_for_namespace(core_v1, apps_v1, batch_v1, ns)
        )
        pods += ns_pods
        deployments += ns_deployments
        jobs += ns_jobs
        statefulsets += ns_statefulsets
        daemonsets += ns_daemonsets
    return pods, deployments, jobs, statefulsets, daemonsets


def get_cluster_info():
    """
    Fetches and returns basic information about the Kubernetes cluster.
    """
    core_v1 = get_k8s_core_v1_client()
    version_v1 = get_k8s_version_api_client()
    apps_v1 = get_k8s_apps_v1_client()
    batch_v1 = get_k8s_batch_v1_client()

    namespaces = get_namespaces(core_v1)
    pods, deployments, jobs, statefulsets, daemonsets = get_all_resources(
        core_v1, apps_v1, batch_v1, namespaces
    )

    cluster_info = {
        "kubernetes_version": get_version_info(version_v1).git_version,
        "components": get_component_status(core_v1),
        "kube_system_pods": get_kube_system_pods_info(core_v1),
        "cluster_id": get_cluster_id(core_v1),
        "cluster_name": get_cluster_name(),
        "nodes": get_nodes(),
        "namespaces": namespaces,
        "pods": pods,
        "deployments": deployments,
        "jobs": jobs,
        "statefulsets": statefulsets,
        "daemonsets": daemonsets,
    }

    return cluster_info
