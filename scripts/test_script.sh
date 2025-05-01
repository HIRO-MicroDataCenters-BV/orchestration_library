#!/bin/bash

CLUSTER_NAME=${1:-sample}

echo "Build Docker image"
docker build -t orchestration-api:alpha1 -f Dockerfile .

echo "Set the kubectl context to $CLUSTER_NAME cluster"
kubectl cluster-info --context kind-$CLUSTER_NAME

echo "Load Image to Kind cluster named '$CLUSTER_NAME'"
kind load docker-image --name $CLUSTER_NAME orchestration-api:alpha1

echo "Deploy the orchestration-api to the Kind cluster"
helm upgrade --install orchestration-api ./charts/orchestration-api \
  --namespace orchestration-api \
  --create-namespace \
  --set orchestration-api.image.repository=orchestration-api \
  --set orchestration-api.image.tag=alpha1
echo "Wait for the orchestration-api to be ready"
kubectl wait --for=condition=available --timeout=60s deployment/orchestration-api -n orchestration-api
echo "Get the orchestration-api service"
kubectl get service -n orchestration-api


