"""
CRUD operations for managing pods in the database.
This module provides functions to create, read, update, and delete pod records.
It uses SQLAlchemy ORM for database interactions.
"""

import kubernetes.client
from kubernetes import config

K8S_IN_USE_NAMESPACE_REGEX = "^kube-.*$|^default$"


def get_k8s_core_v1_client():
    """
    Get the Kubernetes CoreV1 API client.
    This function attempts to load the in-cluster configuration first.
    If it fails, it falls back to loading the kubeconfig file for local development.
    """
    try:
        config.load_incluster_config()
    except config.ConfigException:
        print("Falling back to load_kube_config for local development.")
        config.load_kube_config()

    return kubernetes.client.CoreV1Api()
