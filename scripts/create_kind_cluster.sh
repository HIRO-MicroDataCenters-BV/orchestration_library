#!/bin/bash

CLUSTER_NAME=${1:-sample}
echo "Delete and Create a 'kind' cluster with name '$CLUSTER_NAME'"
kind delete cluster --name $CLUSTER_NAME
# kind create cluster --name $CLUSTER_NAME
kind create cluster --name $CLUSTER_NAME --config - <<EOF
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
networking:
  apiServerAddress: "0.0.0.0" 
  podSubnet: "10.245.0.0/16"
  serviceSubnet: "10.97.0.0/12"
nodes:
  - role: control-plane
    extraPortMappings:
      - containerPort: 30010
        hostPort: 30010
        protocol: TCP
      - containerPort: 30015
        hostPort: 30015
        protocol: TCP
      - containerPort: 30016
        hostPort: 30016
        protocol: TCP
      - containerPort: 30018
        hostPort: 30018
        protocol: TCP
EOF

echo "Set the kubectl context to $CLUSTER_NAME cluster"
kubectl cluster-info --context kind-$CLUSTER_NAME
kubectl config use-context kind-$CLUSTER_NAME
