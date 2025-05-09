import sched
from fastapi.responses import JSONResponse
import kubernetes.client
from kubernetes import client, config


def list_k8s_pods(namespace=None, name=None, id=None, status=None):
    try:
        config.load_incluster_config()
    except config.ConfigException:
        print("Falling back to load_kube_config for local development.")
        config.load_kube_config()

    coreV1 = kubernetes.client.CoreV1Api()
    print("Listing pods with their IPs:")

    if namespace:
        pods = coreV1.list_namespaced_pod(namespace, watch=False)
    else:
        # all namespaces
        pods = coreV1.list_pod_for_all_namespaces(watch=False)

    simplified_pods = []

    for pod in pods.items:
        # Apply filters if any are specified
        if name and pod.metadata.name != name:
            continue
        if id and pod.metadata.uid != id:
            continue
        if status and pod.status.phase != status:
            continue
        if namespace and pod.metadata.namespace != namespace:
            continue
        simplified_pods.append({
            "api_version": pod.api_version,
            "id": pod.metadata.uid,
            "namespace": pod.metadata.namespace,
            "name": pod.metadata.name,
            "labels": pod.metadata.labels,
            "annotations": pod.metadata.annotations,
            "status": pod.status.phase,
            "message": pod.status.message,
            "reason": pod.status.reason,
            "host_ip": pod.status.host_ip,
            "pod_ip": pod.status.pod_ip,
            "start_time": str(pod.status.start_time),
            "node_name": pod.spec.node_name,
            "schedule_name": pod.spec.scheduler_name,
            "containers": [
                {
                    "name": container.name,
                    "image": container.image,
                    "cpu_request": container.resources.requests.get("cpu") if container.resources.requests else None,
                    "memory_request": container.resources.requests.get("memory") if container.resources.requests else None,
                    "cpu_limit": container.resources.limits.get("cpu") if container.resources.limits else None,
                    "memory_limit": container.resources.limits.get("memory") if container.resources.limits else None,
                }
                for container in pod.spec.containers
            ],
        })
    return JSONResponse(content=simplified_pods)
    
   
