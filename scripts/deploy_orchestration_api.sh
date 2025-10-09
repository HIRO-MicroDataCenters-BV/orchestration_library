#!/bin/bash

CLUSTER_NAME=${1:-sample}

KUBERNETES_DASHBOARD_NAMESPACE="aces-kubernetes-dashboard"
KUBERNETES_DASHBOARD_REPO_NAME="aces-kubernetes-dashboard"
KUBERNETES_DASHBOARD_REPO_URL="https://kubernetes.github.io/dashboard/"
KUBERNETES_DASHBOARD_RELEASE_NAME="aces-kubernetes-dashboard"
KUBERNETES_DASHBOARD_RO_SA="readonly-user"
NGINX_DASHBOARD_REVERSE_PROXY_NAME="aces-dashboard-reverse-proxy"
NGINX_DASHBOARD_REVERSE_PROXY_SERVICE_PORT=80
NGINX_DASHBOARD_REVERSE_PROXY_NODE_IP="localhost"
NGINX_DASHBOARD_REVERSE_PROXY_NODE_PORT=30016

ORCHRESTRATION_API_NAMESPACE="aces-orchestration-api"
ORCHRESTRATION_API_RELEASE_NAME="aces-orchestration-api"
ORCHRESTRATION_API_APP_NAME="aces-orchestration-api"
ORCHRESTRATION_API_IMAGE_NAME="orchestration-api"
TIMESTAMP=$(date +%Y%m%d%H%M%S)
ORCHRESTRATION_API_IMAGE_TAG="alpha1-$TIMESTAMP"
ORCHRESTRATION_API_SERVICE_PORT=80
ORCHRESTRATION_API_NODE_PORT=30015

POD_TIMING_WATCHER_NAMESPACE="aces-pod-timing-watcher"
POD_TIMING_WATCHER_RELEASE_NAME="aces-pod-timing-watcher"
POD_TIMING_WATCHER_APP_NAME="aces-pod-timing-watcher"
POD_TIMING_WATCHER_IMAGE_NAME="pod-timing-watcher"
POD_TIMING_WATCHER_IMAGE_TAG="alpha1-$TIMESTAMP"
POD_TIMING_WATCHER_SERVICE_PORT=8080

if [ -z "$CLUSTER_NAME" ]; then
  echo "Usage: $0 <cluster-name> <docker-user> <docker-password>"
  exit 1
fi

echo "Build Docker image for Pod Timing Watcher"
docker build -t $POD_TIMING_WATCHER_IMAGE_NAME:$POD_TIMING_WATCHER_IMAGE_TAG -f service/pod_timing_watcher/Dockerfile service/pod_timing_watcher

echo "Build Docker image for Orchestration API"
docker build -t $ORCHRESTRATION_API_IMAGE_NAME:$ORCHRESTRATION_API_IMAGE_TAG -f Dockerfile .

echo "Set the kubectl context to $CLUSTER_NAME cluster"
kubectl cluster-info --context kind-$CLUSTER_NAME
kubectl config use-context kind-$CLUSTER_NAME

echo "Load Orchestration API Image to Kind cluster named '$CLUSTER_NAME'"
kind load docker-image --name $CLUSTER_NAME $ORCHRESTRATION_API_IMAGE_NAME:$ORCHRESTRATION_API_IMAGE_TAG

echo "Load Pod Timing Watcher Image to Kind cluster named '$CLUSTER_NAME'"
kind load docker-image --name $CLUSTER_NAME $POD_TIMING_WATCHER_IMAGE_NAME:$POD_TIMING_WATCHER_IMAGE_TAG

echo "Add and Update Helm repository for Kubernetes Dashboard"
helm repo add $KUBERNETES_DASHBOARD_REPO_NAME $KUBERNETES_DASHBOARD_REPO_URL
helm repo update

echo "Rebuilding dependencies for orchestration-api chart"
( cd charts/orchestration-api
  rm -f Chart.lock
  helm dependency build
)

# echo "Deploy the Kubernetes Dashboard with reverse proxy to the cluster"
# helm upgrade --install $KUBERNETES_DASHBOARD_RELEASE_NAME ./charts/k8s-dashboard \
#   --namespace $KUBERNETES_DASHBOARD_NAMESPACE \
#   --create-namespace \
#   --set serviceAccountName=$KUBERNETES_DASHBOARD_RO_SA \
#   --set reverseProxy.name=$NGINX_DASHBOARD_REVERSE_PROXY_NAME \
#   --set reverseProxy.service.port=$NGINX_DASHBOARD_REVERSE_PROXY_SERVICE_PORT \
#   --set reverseProxy.service.type=NodePort \
#   --set reverseProxy.service.nodePort=$NGINX_DASHBOARD_REVERSE_PROXY_NODE_PORT \

echo "Deploy the orchestration-api with dependencies(K8S Dashboard with reverse proxy) to the Kind cluster"
RELEASE_NAME=$ORCHRESTRATION_API_RELEASE_NAME
helm upgrade --install $ORCHRESTRATION_API_RELEASE_NAME ./charts/orchestration-api \
  --post-renderer ./charts/orchestration-api/add-common-labels.sh \
  --namespace $ORCHRESTRATION_API_NAMESPACE \
  --create-namespace \
  --set app.image.repository=$ORCHRESTRATION_API_IMAGE_NAME \
  --set app.image.tag=$ORCHRESTRATION_API_IMAGE_TAG \
  --set app.image.pullPolicy=IfNotPresent \
  --set k8sDashboard.enabled=true \
  --set k8sDashboard.namespace=$KUBERNETES_DASHBOARD_NAMESPACE \
  --set k8sDashboard.serviceAccountName=$KUBERNETES_DASHBOARD_RO_SA \
  --set k8sDashboard.reverseProxy.service.type=NodePort \
  --set k8sDashboard.reverseProxy.service.port=$NGINX_DASHBOARD_REVERSE_PROXY_SERVICE_PORT \
  --set k8sDashboard.reverseProxy.service.name=$NGINX_DASHBOARD_REVERSE_PROXY_NAME \
  --set k8sDashboard.reverseProxy.service.nodePort=$NGINX_DASHBOARD_REVERSE_PROXY_NODE_PORT \
  --set k8sDashboard.accessURL="http://${NGINX_DASHBOARD_REVERSE_PROXY_NODE_IP}:${NGINX_DASHBOARD_REVERSE_PROXY_NODE_PORT}/" \
  --set app.service.type=NodePort \
  --set app.service.port=$ORCHRESTRATION_API_SERVICE_PORT \
  --set app.service.nodePort=$ORCHRESTRATION_API_NODE_PORT \
  --set runMigration=true \
  --set podTimingWatcher.enabled=true \
  --set podTimingWatcher.image.repository=$POD_TIMING_WATCHER_IMAGE_NAME \
  --set podTimingWatcher.image.tag=$POD_TIMING_WATCHER_IMAGE_TAG \
  --set podTimingWatcher.image.pullPolicy=IfNotPresent
  # set to pullPolicy=IfNotPresent to avoid pulling the image from the registry only for kind cluster
  # set dummyRedeployTimestamp to force redeploy

echo "Wait for the $ORCHRESTRATION_API_APP_NAME to be ready"
kubectl wait --for=condition=available --timeout=60s deployment/$ORCHRESTRATION_API_APP_NAME -n $ORCHRESTRATION_API_NAMESPACE --context kind-$CLUSTER_NAME

echo "Get the $ORCHRESTRATION_API_APP_NAME service"
kubectl get service -n $ORCHRESTRATION_API_APP_NAME --context kind-$CLUSTER_NAME

# echo "Deploy the Pod Timing Watcher to Kind cluster"
# RELEASE_NAME=$POD_TIMING_WATCHER_RELEASE_NAME
# helm upgrade --install $RELEASE_NAME ./charts/pod-timing-watcher \
#   --namespace $POD_TIMING_WATCHER_NAMESPACE \
#   --create-namespace \
#   --set image.repository=$POD_TIMING_WATCHER_IMAGE_NAME \
#   --set image.tag=$POD_TIMING_WATCHER_IMAGE_TAG \
#   --set image.pullPolicy=IfNotPresent \
#   --set service.port=$POD_TIMING_WATCHER_SERVICE_PORT \

# echo "Wait for the $POD_TIMING_WATCHER_APP_NAME to be ready"
# kubectl wait --for=condition=available --timeout=60s deployment/$POD_TIMING_WATCHER_APP_NAME -n $POD_TIMING_WATCHER_NAMESPACE --context kind-$CLUSTER_NAME

# echo "Get the $POD_TIMING_WATCHER_APP_NAME service"
# kubectl get service -n $POD_TIMING_WATCHER_APP_NAME --context kind-$CLUSTER_NAME

