"""
Get the parent controller of a Kubernetes pod.
"""

from app.repositories.k8s.k8s_common import (
    get_k8s_apps_v1_client,
    get_k8s_batch_v1_client,
    get_k8s_core_v1_client
)


def get_parent_controller_details_of_pod(namespace, pod_name, pod_id):
    """
    Get the parent controller of a Kubernetes pod.
    Args:
        pod_name (str): Name of the pod.
        namespace (str): Namespace of the pod.
    Returns:
        dict: Details of the parent controller (Deployment, StatefulSet, DaemonSet, or Job).
    """

    core_v1 = get_k8s_core_v1_client()
    apps_v1 = get_k8s_apps_v1_client()
    batch_v1 = get_k8s_batch_v1_client()

    if not pod_name and not pod_id:
        raise ValueError("Either pod_name or pod_id must be provided.")

    pod = None  # Initialize pod to None

    if pod_name:
        pod = core_v1.read_namespaced_pod(name=pod_name, namespace=namespace)
    elif pod_id:
        pod_list = core_v1.list_namespaced_pod(namespace=namespace)
        for p in pod_list.items:
            if p.metadata.uid == pod_id:
                pod = p
                break
        if not pod:
            return {
                "message": f"No pod found with UID: {pod_id} in namespace: {namespace}"
            }

    if not pod.metadata.owner_references:
        return {"message": "Pod has no owner references (standalone pod)"}

    for owner in pod.metadata.owner_references:
        if owner.kind == "ReplicaSet":
            # Likely a Deployment-managed pod
            rs = apps_v1.read_namespaced_replica_set(
                name=owner.name, namespace=namespace
            )
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

        elif owner.kind == "StatefulSet":
            statefulset = apps_v1.read_namespaced_stateful_set(
                name=owner.name, namespace=namespace
            )
            return {
                "name": statefulset.metadata.name,
                "namespace": statefulset.metadata.namespace,
                "api_version": statefulset.api_version,
                "kind": "StatefulSet",
                "current_scale": statefulset.spec.replicas,
            }

        elif owner.kind == "DaemonSet":
            daemonset = apps_v1.read_namespaced_daemon_set(
                name=owner.name, namespace=namespace
            )
            return {
                "name": daemonset.metadata.name,
                "namespace": daemonset.metadata.namespace,
                "api_version": daemonset.api_version,
                "kind": "DaemonSet",
                "current_scale": daemonset.status.desired_number_scheduled,
            }

        elif owner.kind == "Job":
            job = batch_v1.read_namespaced_job(name=owner.name, namespace=namespace)
            return {
                "name": job.metadata.name,
                "namespace": job.metadata.namespace,
                "api_version": job.api_version,
                "kind": "Job",
                "current_scale": job.spec.parallelism or 1,
            }

    return {
        "message": "No known controller found (Deployment, StatefulSet, DaemonSet, or Job)"
    }
