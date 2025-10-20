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

WORKLOAD_TIMING_WATCHER_NAMESPACE="aces-workload-timing-watcher"
WORKLOAD_TIMING_WATCHER_RELEASE_NAME="aces-workload-timing-watcher"
WORKLOAD_TIMING_WATCHER_APP_NAME="aces-workload-timing-watcher"
WORKLOAD_TIMING_WATCHER_IMAGE_NAME="workload-timing-watcher"
WORKLOAD_TIMING_WATCHER_IMAGE_TAG="alpha1-$TIMESTAMP"
WORKLOAD_TIMING_WATCHER_SERVICE_PORT=8080

ALERTS_POPULATOR_NAMESPACE="aces-alerts-populator"
ALERTS_POPULATOR_RELEASE_NAME="aces-alerts-populator"
ALERTS_POPULATOR_APP_NAME="aces-alerts-populator"
ALERTS_POPULATOR_IMAGE_NAME="alerts-populator"
ALERTS_POPULATOR_IMAGE_TAG="alpha1-$TIMESTAMP"
ALERTS_POPULATOR_SERVICE_PORT=8080
# ALERTS_POPULATOR_NATS_SERVER="nats://demo.nats.io:4222"
ALERTS_POPULATOR_NATS_SERVER=nats://nats-server.aces-monitoring-observability.svc.cluster.local:4222
# ALERTS_POPULATOR_NATS_TOPICS=("alerts.network-attack" "alerts.abnormal")
ALERTS_POPULATOR_NATS_JS_STREAM="PREDICTIONS"
ALERTS_POPULATOR_NATS_JS_SUBJECTS=("anomalies" "network-attacks")
ALERTS_POPULATOR_NATS_JS_DURABLE="alerts-populator"
ALERTS_POPULATOR_ALERTS_API_URL="http://$ORCHRESTRATION_API_APP_NAME.$ORCHRESTRATION_API_NAMESPACE.svc.cluster.local:$ORCHRESTRATION_API_SERVICE_PORT/alerts"

if [ -z "$CLUSTER_NAME" ]; then
  echo "Usage: $0 <cluster-name> <docker-user> <docker-password>"
  exit 1
fi

echo "Build Docker image for Workload Timing Watcher"
docker build -t $WORKLOAD_TIMING_WATCHER_IMAGE_NAME:$WORKLOAD_TIMING_WATCHER_IMAGE_TAG -f service/workload-timing-watcher/Dockerfile service/workload-timing-watcher

echo "Build Docker image for Alerts Populator"
docker build -t $ALERTS_POPULATOR_IMAGE_NAME:$ALERTS_POPULATOR_IMAGE_TAG -f service/alerts-populator/Dockerfile service/alerts-populator

echo "Build Docker image for Orchestration API"
docker build -t $ORCHRESTRATION_API_IMAGE_NAME:$ORCHRESTRATION_API_IMAGE_TAG -f Dockerfile .

echo "Set the kubectl context to $CLUSTER_NAME cluster"
kubectl cluster-info --context kind-$CLUSTER_NAME
kubectl config use-context kind-$CLUSTER_NAME

echo "Load Orchestration API Image to Kind cluster named '$CLUSTER_NAME'"
kind load docker-image --name $CLUSTER_NAME $ORCHRESTRATION_API_IMAGE_NAME:$ORCHRESTRATION_API_IMAGE_TAG

echo "Load Workload Timing Watcher Image to Kind cluster named '$CLUSTER_NAME'"
kind load docker-image --name $CLUSTER_NAME $WORKLOAD_TIMING_WATCHER_IMAGE_NAME:$WORKLOAD_TIMING_WATCHER_IMAGE_TAG

echo "Load Alerts Populator Image to Kind cluster named '$CLUSTER_NAME'"
kind load docker-image --name $CLUSTER_NAME $ALERTS_POPULATOR_IMAGE_NAME:$ALERTS_POPULATOR_IMAGE_TAG

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

# Prepare JetStream NATS locally (host) so Kind cluster can use it.
# Mac/Kind: pods can reach host via host.docker.internal
NATS_CONTAINER_NAME="${ALERTS_POPULATOR_NATS_JS_DURABLE}-nats-js"
echo "Check if local NATS JetStream container '${NATS_CONTAINER_NAME}' is running"
if ! docker ps --format '{{.Names}}' | grep -q "^${NATS_CONTAINER_NAME}$"; then
  echo "Starting local NATS JetStream container '${NATS_CONTAINER_NAME}'"
  docker run -d --name ${NATS_CONTAINER_NAME} \
    -p 4222:4222 -p 6222:6222 -p 8222:8222 \
    nats:2.10 -js
else
  echo "NATS JetStream container '${NATS_CONTAINER_NAME}' already running"
fi

# Ensure stream exists (uses nats-box + nats CLI)
echo "Ensuring JetStream stream '${ALERTS_POPULATOR_NATS_JS_STREAM}' exists"
SUBJECTS_CSV="$(printf "%s," "${ALERTS_POPULATOR_NATS_JS_SUBJECTS[@]}" | sed 's/,$//')"
echo "Subjects for the stream: ${SUBJECTS_CSV}"

# Create stream if not exists
for subject in "${ALERTS_POPULATOR_NATS_JS_SUBJECTS[@]}"; do
  echo "JetStream subject: $subject"
  # Check first
  docker run --rm --network host natsio/nats-box \
    nats --server nats://localhost:4222 stream info "${ALERTS_POPULATOR_NATS_JS_STREAM}" >/dev/null 2>&1
  if [ $? -ne 0 ]; then
    echo "Creating stream ${ALERTS_POPULATOR_NATS_JS_STREAM} with subjects: ${SUBJECTS_CSV}"
    docker run --rm --network host natsio/nats-box \
      nats --server nats://localhost:4222 stream add "${ALERTS_POPULATOR_NATS_JS_STREAM}" \
        --subjects "${SUBJECTS_CSV}" \
        --storage memory \
        --retention limits \
        --discard old \
        --dupe-window 2m \
        --max-msgs=-1 --max-bytes=-1 --replicas=1 --allow-rollup --no-allow-direct \
        --defaults || echo "Stream creation failed"
  else
    echo "Stream ${ALERTS_POPULATOR_NATS_JS_STREAM} already exists"
  fi
done

# Override NATS server to point to host JetStream (instead of in-cluster nats)
ALERTS_POPULATOR_NATS_SERVER="nats://host.docker.internal:4222"


# Prepare --set arguments for NATS_TOPICS array
# nats_topics_set=""
# for i in "${!ALERTS_POPULATOR_NATS_TOPICS[@]}"; do
#   nats_topics_set+="--set alertsPopulator.env.NATS_TOPICS[$i]=${ALERTS_POPULATOR_NATS_TOPICS[$i]} "
# done
# nats_topics_set=${nats_topics_set% }  # Remove trailing space

nats_js_subjects=""
for i in "${!ALERTS_POPULATOR_NATS_JS_SUBJECTS[@]}"; do
  nats_js_subjects+="--set alertsPopulator.env.NATS_JS_SUBJECTS[$i]=${ALERTS_POPULATOR_NATS_JS_SUBJECTS[$i]} "
done
nats_js_subjects=${nats_js_subjects% }  # Remove trailing space

echo "Deploy the orchestration-api with dependencies(K8S Dashboard with reverse proxy) to the Kind cluster"
RELEASE_NAME=$ORCHRESTRATION_API_RELEASE_NAME
helm_command="""helm upgrade --install $ORCHRESTRATION_API_RELEASE_NAME ./charts/orchestration-api \
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
  --set workloadTimingWatcher.enabled=true \
  --set workloadTimingWatcher.image.repository=$WORKLOAD_TIMING_WATCHER_IMAGE_NAME \
  --set workloadTimingWatcher.image.tag=$WORKLOAD_TIMING_WATCHER_IMAGE_TAG \
  --set workloadTimingWatcher.image.pullPolicy=IfNotPresent \
  --set alertsPopulator.enabled=true \
  --set alertsPopulator.image.repository=$ALERTS_POPULATOR_IMAGE_NAME \
  --set alertsPopulator.image.tag=$ALERTS_POPULATOR_IMAGE_TAG \
  --set alertsPopulator.image.pullPolicy=IfNotPresent \
  --set alertsPopulator.env.NATS_SERVER=$ALERTS_POPULATOR_NATS_SERVER \
  --set alertsPopulator.env.NATS_JS_STREAM=$ALERTS_POPULATOR_NATS_JS_STREAM \
  --set alertsPopulator.env.NATS_JS_DURABLE=$ALERTS_POPULATOR_NATS_JS_DURABLE \
  ${nats_js_subjects} \
  --set alertsPopulator.env.ALERTS_API_URL=$ALERTS_POPULATOR_ALERTS_API_URL
  """
# echo "Helm command: $helm_command"
eval $helm_command
  # set to pullPolicy=IfNotPresent to avoid pulling the image from the registry only for kind cluster
  # set dummyRedeployTimestamp to force redeploy

echo "Wait for the $ORCHRESTRATION_API_APP_NAME to be ready"
kubectl wait --for=condition=available --timeout=60s deployment/$ORCHRESTRATION_API_APP_NAME -n $ORCHRESTRATION_API_NAMESPACE --context kind-$CLUSTER_NAME

echo "Get the $ORCHRESTRATION_API_APP_NAME service"
kubectl get service -n $ORCHRESTRATION_API_APP_NAME --context kind-$CLUSTER_NAME

# echo "Deploy the Workload Timing Watcher to Kind cluster"
# RELEASE_NAME=$WORKLOAD_TIMING_WATCHER_RELEASE_NAME
# helm upgrade --install $RELEASE_NAME ./charts/workload-timing-watcher \
#   --namespace $WORKLOAD_TIMING_WATCHER_NAMESPACE \
#   --create-namespace \
#   --set image.repository=$WORKLOAD_TIMING_WATCHER_IMAGE_NAME \
#   --set image.tag=$WORKLOAD_TIMING_WATCHER_IMAGE_TAG \
#   --set image.pullPolicy=IfNotPresent \
#   --set service.port=$WORKLOAD_TIMING_WATCHER_SERVICE_PORT \

# echo "Wait for the $WORKLOAD_TIMING_WATCHER_APP_NAME to be ready"
# kubectl wait --for=condition=available --timeout=60s deployment/$WORKLOAD_TIMING_WATCHER_APP_NAME -n $WORKLOAD_TIMING_WATCHER_NAMESPACE --context kind-$CLUSTER_NAME

# echo "Get the $WORKLOAD_TIMING_WATCHER_APP_NAME service"
# kubectl get service -n $WORKLOAD_TIMING_WATCHER_APP_NAME --context kind-$CLUSTER_NAME

