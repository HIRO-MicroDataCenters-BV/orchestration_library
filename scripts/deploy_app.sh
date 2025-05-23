#!/bin/bash

CLUSTER_NAME=${1:-sample}

if [ -z "$CLUSTER_NAME" ]; then
  echo "Usage: $0 <cluster-name> <docker-user> <docker-password>"
  exit 1
fi

echo "Build Docker image"
docker build -t orchestration-api:alpha1 -f Dockerfile .

echo "Set the kubectl context to $CLUSTER_NAME cluster"
kubectl cluster-info --context kind-$CLUSTER_NAME
kubectl config use-context kind-$CLUSTER_NAME

echo "Load Image to Kind cluster named '$CLUSTER_NAME'"
kind load docker-image --name $CLUSTER_NAME orchestration-api:alpha1

echo "Deploy the orchestration-api to the Kind cluster"
helm upgrade --install orchestration-api ./charts/orchestration-api \
  --namespace orchestration-api \
  --create-namespace \
  --set app.image.repository=orchestration-api \
  --set app.image.tag=alpha1 \
  --set namespace=orchestration-api \
  --set app.image.pullPolicy=IfNotPresent \
  --set runMigration=false \
  --set dummyRedeployTimestamp=$(date +%s)  
  # set to pullPolicy=IfNotPresent to avoid pulling the image from the registry only for kind cluster
  # set dummyRedeployTimestamp to force redeploy

echo "Wait for the orchestration-api to be ready"
kubectl wait --for=condition=available --timeout=60s deployment/orchestration-api -n orchestration-api --context kind-$CLUSTER_NAME

echo "Get the orchestration-api service"
kubectl get service -n orchestration-api --context kind-$CLUSTER_NAME

