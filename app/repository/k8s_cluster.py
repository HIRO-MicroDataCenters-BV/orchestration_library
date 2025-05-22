from pick import pick  # install pick using `pip install pick`

from kubernetes import client, config
from kubernetes.client import configuration


def list_cluster_info(namespace=None, name=None, id=None, status=None):
    """
    List all nodes in the cluster.
    If no filters are specified, list all nodes.
    """

    try:
        # Load in-cluster configuration
        config.load_incluster_config()
    except config.ConfigException:
        # Fallback to local kubeconfig for development
        print("Falling back to load_kube_config for local development.")
        config.load_kube_config()

    coreV1 = kubernetes.client.CoreV1Api()
    print("Listing cluster with the  details:")
    contexts, active_context = config.list_kube_config_contexts()
    if not contexts:
        print("Cannot find any context in kube-config file.")
        return
    contexts = [context['name'] for context in contexts]
    active_index = contexts.index(active_context['name'])
    cluster_name, first_index = pick(contexts, title="Pick the first context",
                                     default_index=active_index)
    # cluster2, _ = pick(contexts, title="Pick the second context", default_index=first_index)

    client1 = client.CoreV1Api(
        api_client=config.new_client_from_config(context=cluster_name))
    # client2 = client.CoreV1Api(api_client=config.new_client_from_config(context=cluster2))

    print("\nList of pods on %s:" % cluster_name)
    for i in client1.list_pod_for_all_namespaces().items:
        print("%s\t%s\t%s" %
              (i.status.pod_ip, i.metadata.namespace, i.metadata.name))


'''
        print("\n\nList of pods on %s:" % cluster2)
        for i in client2.list_pod_for_all_namespaces().items:
            print("%s\t%s\t%s" %
                  (i.status.pod_ip, i.metadata.namespace, i.metadata.name))
'''
