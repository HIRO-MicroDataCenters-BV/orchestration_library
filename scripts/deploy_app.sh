#!/bin/bash

CLUSTER_NAME=${1:-sample}
KUBERNETES_DASHBOARD_NAMESPACE="kubernetes-dashboard"
KUBERNETES_DASHBOARD_REPO_NAME="kubernetes-dashboard"
KUBERNETES_DASHBOARD_REPO_URL="https://kubernetes.github.io/dashboard/"
KUBERNETES_DASHBOARD_CHART_NAME="kubernetes-dashboard"
KUBERNETES_DASHBOARD_RELEASE_NAME="kubernetes-dashboard"
ORCHRESTRATION_API_NAMESPACE="orchestration-api"
ORCHRESTRATION_API_RELEASE_NAME="orchestration-api"
ORCHRESTRATION_API_APP_NAME="orchestration-api"
ORCHRESTRATION_API_IMAGE_NAME="orchestration-api"
ORCHRESTRATION_API_IMAGE_TAG="alpha1"

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
kind load docker-image --name $CLUSTER_NAME $ORCHRESTRATION_API_IMAGE_NAME:$ORCHRESTRATION_API_IMAGE_TAG

echo "Add and Update Helm repository for Kubernetes Dashboard"
helm repo add $KUBERNETES_DASHBOARD_REPO_NAME $KUBERNETES_DASHBOARD_REPO_URL
helm repo update

echo "Deploy the Kubernetes Dashboard to the Kind cluster"
helm upgrade --install $KUBERNETES_DASHBOARD_RELEASE_NAME $KUBERNETES_DASHBOARD_REPO_NAME/$KUBERNETES_DASHBOARD_CHART_NAME \
  --namespace $KUBERNETES_DASHBOARD_NAMESPACE \
  --create-namespace \
  --set protocolHttp=true

echo "Update Helm dependencies for orchestration-api chart"
helm dependency build ./charts/orchestration-api

echo "Deploy the orchestration-api to the Kind cluster"
helm upgrade --install $ORCHRESTRATION_API_RELEASE_NAME ./charts/orchestration-api \
  --namespace $ORCHRESTRATION_API_NAMESPACE \
  --create-namespace \
  --set app.image.repository=$ORCHRESTRATION_API_IMAGE_NAME \
  --set app.image.tag=$ORCHRESTRATION_API_IMAGE_TAG \
  --set app.name=$ORCHRESTRATION_API_APP_NAME \
  --set namespace=$ORCHRESTRATION_API_NAMESPACE \
  --set dashboard.namespace=$KUBERNETES_DASHBOARD_NAMESPACE \
  --set app.image.pullPolicy=IfNotPresent \
  --set runMigration=true \
  --set dummyRedeployTimestamp=$(date +%s)  
  # set to pullPolicy=IfNotPresent to avoid pulling the image from the registry only for kind cluster
  # set dummyRedeployTimestamp to force redeploy

echo "Wait for the orchestration-api to be ready"
kubectl wait --for=condition=available --timeout=60s deployment/$ORCHRESTRATION_API_APP_NAME -n $ORCHRESTRATION_API_NAMESPACE --context kind-$CLUSTER_NAME

echo "Get the orchestration-api service"
kubectl get service -n orchestration-api --context kind-$CLUSTER_NAME

