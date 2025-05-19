"""
CRUD operations for managing pods in the database.
This module provides functions to create, read, update, and delete pod records.
It uses SQLAlchemy ORM for database interactions.
"""

import kubernetes.client
from kubernetes import config

K8S_IN_USE_NAMESPACE_REGEX = "^kube-.*$|^default$"

def load_kube_config():
    """
    Load the kubeconfig file for local development.
    This function attempts to load the in-cluster configuration first.
    If it fails, it falls back to loading the kubeconfig file for local development.
    """
    try:
        config.load_incluster_config()
    except config.ConfigException:
        print("Falling back to load_kube_config for local development.")
        config.load_kube_config()

def get_k8s_core_v1_client():
    """
    Get the Kubernetes CoreV1 API client.
    """
    load_kube_config()
    return kubernetes.client.CoreV1Api()

def get_k8s_custom_objects_client():
    """
    Get the Kubernetes Custom Objects API client.
    """
    load_kube_config()
    return kubernetes.client.CustomObjectsApi()

def get_k8s_version_api_client():
    """
    Get the Kubernetes Version API client.
    """
    load_kube_config()
    return kubernetes.client.VersionApi()

def get_k8s_apps_v1_client():
    """
    Get the Kubernetes AppsV1 API client.
    """
    load_kube_config()
    return kubernetes.client.AppsV1Api()

def get_k8s_batch_v1_client():
    """
    Get the Kubernetes BatchV1 API client.
    """
    load_kube_config()
    return kubernetes.client.BatchV1Api()
