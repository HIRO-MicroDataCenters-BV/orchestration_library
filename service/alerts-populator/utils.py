from functools import lru_cache
from typing import Optional, List, Dict
from kubernetes import client, config
from kubernetes.config.config_exception import ConfigException


def _load_kube_config():
    """
    Load in-cluster config if available; fall back to local kubeconfig (for dev).
    """
    try:
        config.load_incluster_config()
    except ConfigException:
        config.load_kube_config()


@lru_cache(maxsize=1)
def get_nodes() -> List[Dict[str, Optional[str]]]:
    """
    Returns a list of node dicts: {'id': <node_name>, 'ip': <InternalIP>}.

    Result cached (invalidate by restarting pod).
    """
    _load_kube_config()
    v1 = client.CoreV1Api()
    nodes: List[Dict[str, Optional[str]]] = []
    for item in v1.list_node().items:
        node_name = item.metadata.name
        node_id = item.metadata.uid
        internal_ip = next(
            (addr.address for addr in item.status.addresses if addr.type == "InternalIP"),
            None,
        )
        nodes.append({"id": node_id, "name": node_name, "ip": internal_ip})
    return nodes


def get_node_by_ip(ip: str) -> Optional[Dict[str, Optional[str]]]:
    """
    Reverse lookup: given an InternalIP return {'id': node_name, 'ip': ip} or None.
    """
    if not ip:
        return None
    for node in get_nodes():
        if node["ip"] == ip:
            return node
    return None


def get_node_name_by_ip(ip: str) -> Optional[str]:
    """
    Convenience: return node name for an InternalIP or None.
    """
    node = get_node_by_ip(ip)
    return node["name"] if node else None

def get_node_id_by_ip(ip: str) -> Optional[str]:
    """
    Convenience: return node ID for an InternalIP or None.
    """
    node = get_node_by_ip(ip)
    return node["id"] if node else None

def get_node_id_by_name(node_name: str) -> Optional[str]:
    """
    Convenience: return node ID for a node name or None.
    """
    if not node_name:
        return None
    for node in get_nodes():
        if node["name"] == node_name:
            return node["id"]

def get_pod_id_by_name(pod_name: str) -> Optional[str]:
    """
    Convenience: return pod ID for a pod name (searching all namespaces) or None.
    """
    if not pod_name:
        return None
    _load_kube_config()
    v1 = client.CoreV1Api()
    try:
        pods = v1.list_pod_for_all_namespaces(field_selector=f"metadata.name={pod_name}")
        for pod in pods.items:
            if pod.metadata.name == pod_name:
                return pod.metadata.uid
        return None
    except client.exceptions.ApiException:
        return None