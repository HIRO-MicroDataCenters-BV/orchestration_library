from pick import pick  # install pick using `pip install pick`

from kubernetes import client, config
from kubernetes.client import configuration


def list_cluster_info(cluster_name):
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
