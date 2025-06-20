#!/bin/bash

CLUSTER_NAME=${1:-sample}

KUBERNETES_DASHBOARD_NAMESPACE="aces-kubernetes-dashboard"
KUBERNETES_DASHBOARD_REPO_NAME="aces-kubernetes-dashboard"
KUBERNETES_DASHBOARD_REPO_URL="https://kubernetes.github.io/dashboard/"
KUBERNETES_DASHBOARD_RELEASE_NAME="aces-kubernetes-dashboard"
KUBERNETES_DASHBOARD_RO_SA="readonly-user"
NGINX_DASHBOARD_REVERSE_PROXY_NAME="aces-dashboard-reverse-proxy"
NGINX_DASHBOARD_REVERSE_PROXY_SERVICE_PORT=80
NGINX_DASHBOARD_REVERSE_PROXY_NODE_PORT=30016

ORCHRESTRATION_API_NAMESPACE="aces-orchestration-api"
ORCHRESTRATION_API_RELEASE_NAME="aces-orchestration-api"
ORCHRESTRATION_API_APP_NAME="aces-orchestration-api"
ORCHRESTRATION_API_IMAGE_NAME="orchestration-api"
ORCHRESTRATION_API_IMAGE_TAG="alpha1"
ORCHRESTRATION_API_SERVICE_PORT=80
ORCHRESTRATION_API_NODE_PORT=30015

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

echo "Update Helm dependencies for k8s-dashboard chart"
helm dependency build ./charts/k8s-dashboard

echo "Deploy the Kubernetes Dashboard with reverse proxy to the cluster"
helm upgrade --install $KUBERNETES_DASHBOARD_RELEASE_NAME ./charts/k8s-dashboard \
  --namespace $KUBERNETES_DASHBOARD_NAMESPACE \
  --create-namespace \
  --set namespace=$KUBERNETES_DASHBOARD_NAMESPACE \
  --set serviceAccountName=$KUBERNETES_DASHBOARD_RO_SA \
  --set reverseProxy.name=$NGINX_DASHBOARD_REVERSE_PROXY_NAME \
  --set reverseProxy.service.port=$NGINX_DASHBOARD_REVERSE_PROXY_SERVICE_PORT \
  --set reverseProxy.service.nodePort=$NGINX_DASHBOARD_REVERSE_PROXY_NODE_PORT \
  # --set reverseProxy.service.type=NodePort \


echo "Deploy the orchestration-api to the Kind cluster"
helm upgrade --install $ORCHRESTRATION_API_RELEASE_NAME ./charts/orchestration-api \
  --namespace $ORCHRESTRATION_API_NAMESPACE \
  --create-namespace \
  --set app.image.repository=$ORCHRESTRATION_API_IMAGE_NAME \
  --set app.image.tag=$ORCHRESTRATION_API_IMAGE_TAG \
  --set namespace=$ORCHRESTRATION_API_NAMESPACE \
  --set app.image.pullPolicy=IfNotPresent \
  --set dashboard.namespace=$KUBERNETES_DASHBOARD_NAMESPACE \
  --set dashboard.serviceAccountName=$KUBERNETES_DASHBOARD_RO_SA \
  --set dashboard.reverseProxyServiceName=$NGINX_DASHBOARD_REVERSE_PROXY_NAME \
  --set dashboard.reverseProxyServicePort=$NGINX_DASHBOARD_REVERSE_PROXY_SERVICE_PORT \
  --set app.service.port=$ORCHRESTRATION_API_SERVICE_PORT \
  --set app.service.nodePort=$ORCHRESTRATION_API_NODE_PORT \
  --set runMigration=true \
  --set dummyRedeployTimestamp=$(date +%s)
  # --set app.service.type=NodePort \
  # set to pullPolicy=IfNotPresent to avoid pulling the image from the registry only for kind cluster
  # set dummyRedeployTimestamp to force redeploy

echo "Wait for the $ORCHRESTRATION_API_APP_NAME to be ready"
kubectl wait --for=condition=available --timeout=60s deployment/$ORCHRESTRATION_API_APP_NAME -n $ORCHRESTRATION_API_NAMESPACE --context kind-$CLUSTER_NAME

echo "Get the $ORCHRESTRATION_API_APP_NAME service"
kubectl get service -n $ORCHRESTRATION_API_APP_NAME --context kind-$CLUSTER_NAME

