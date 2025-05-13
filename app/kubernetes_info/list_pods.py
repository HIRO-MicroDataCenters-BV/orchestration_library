#!/usr/bin/python3.7
# Script name: list_pods_1.py
# pip install kubernetes
import kubernetes.client
from kubernetes import client, config

# config.load_incluster_config()
# config.load_kube_config("/root/config")


def list_pod_for_all_namespaces():
    config.load_kube_config()

    v1 = kubernetes.client.CoreV1Api()
    print("Listing pods with their IPs:")

    # ret = v1.list_pod_for_all_namespaces(watch=False)
    # a specific namespace
    #  ret = v1.list_namespaced_pod(namespace="dev", watch=False)
    ret = v1.list_pod_for_all_namespaces(watch=False)

    for i in ret.items:
        print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))
