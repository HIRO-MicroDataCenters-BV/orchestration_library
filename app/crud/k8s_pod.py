import sched
from fastapi.responses import JSONResponse
import kubernetes.client
from kubernetes import client, config


def list_k8s_pods(namespace=None):
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
        })
    return JSONResponse(content=simplified_pods)
    
   
