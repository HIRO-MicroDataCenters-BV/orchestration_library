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
            "id": pod.metadata.uid,
            "namespace": pod.metadata.namespace,
            "api_version": pod.api_version,
            "name": pod.metadata.name,
            "status": pod.status.phase,
            "node_name": pod.spec.node_name,
            "start_time": str(pod.status.start_time)
        })
    return JSONResponse(content=simplified_pods)
    
   
