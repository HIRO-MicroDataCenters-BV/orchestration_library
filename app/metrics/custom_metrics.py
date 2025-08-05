"""
Custom metrics for the application.
"""
from prometheus_client import Counter, Histogram

# General API metrics
api_requests_total = Counter(
    "api_requests_total",
    "Total number of API requests",
    ["method", "endpoint", "status_code", "exception"]
)
api_requests_latency_seconds = Histogram(
    "api_requests_latency_seconds",
    "Latency of API requests in seconds",
    ["method", "endpoint", "status_code", "exception"]
)

# Workload Action API
workload_action_requests_total = Counter(
    "workload_action_requests_total",
    "Total number of workload action requests",
    ["method", "endpoint", "status_code", "exception"]
)
workload_action_requests_latency_seconds = Histogram(
    "workload_action_requests_latency_seconds",
    "Latency of workload action requests in seconds",
    ["method", "endpoint", "status_code", "exception"]
)

# Alerts API
alerts_requests_total = Counter(
    "alerts_requests_total",
    "Total number of alerts API requests",
    ["method", "endpoint", "status_code", "exception"]
)
alerts_requests_latency_seconds = Histogram(
    "alerts_requests_latency_seconds",
    "Latency of alerts API requests in seconds",
    ["method", "endpoint", "status_code", "exception"]
)

# Tuning Parameters API
tuning_parameters_requests_total = Counter(
    "tuning_parameters_requests_total",
    "Total number of tuning parameters API requests",
    ["method", "endpoint", "status_code", "exception"]
)
tuning_parameters_requests_latency_seconds = Histogram(
    "tuning_parameters_requests_latency_seconds",
    "Latency of tuning parameters API requests in seconds",
    ["method", "endpoint", "status_code", "exception"]
)

# Workload Request Decision API
workload_request_decision_requests_total = Counter(
    "workload_request_decision_requests_total",
    "Total number of workload request decision API requests",
    ["method", "endpoint", "status_code", "exception"]
)
workload_request_decision_requests_latency_seconds = Histogram(
    "workload_request_decision_requests_latency_seconds",
    "Latency of workload request decision API requests in seconds",
    ["method", "endpoint", "status_code", "exception"]
)

# Workload Flow API
workload_flow_requests_total = Counter(
    "workload_flow_requests_total",
    "Total number of workload flow API requests",
    ["method", "endpoint", "status_code", "exception"]
)
workload_flow_requests_latency_seconds = Histogram(
    "workload_flow_requests_latency_seconds",
    "Latency of workload flow API requests in seconds",
    ["method", "endpoint", "status_code", "exception"]
)

# K8s Pod API
k8s_pod_requests_total = Counter(
    "k8s_pod_requests_total",
    "Total number of k8s pod API requests",
    ["method", "endpoint", "status_code", "exception"]
)
k8s_pod_requests_latency_seconds = Histogram(
    "k8s_pod_requests_latency_seconds",
    "Latency of k8s pod API requests in seconds",
    ["method", "endpoint", "status_code", "exception"]
)

# K8s Pod Parent API
k8s_pod_parent_requests_total = Counter(
    "k8s_pod_parent_requests_total",
    "Total number of k8s pod parent API requests",
    ["method", "endpoint", "status_code", "exception"]
)
k8s_pod_parent_requests_latency_seconds = Histogram(
    "k8s_pod_parent_requests_latency_seconds",
    "Latency of k8s pod parent API requests in seconds",
    ["method", "endpoint", "status_code", "exception"]
)

# K8s User Pod API
k8s_user_pod_requests_total = Counter(
    "k8s_user_pod_requests_total",
    "Total number of k8s user pod API requests",
    ["method", "endpoint", "status_code", "exception"]
)
k8s_user_pod_requests_latency_seconds = Histogram(
    "k8s_user_pod_requests_latency_seconds",
    "Latency of k8s user pod API requests in seconds",
    ["method", "endpoint", "status_code", "exception"]
)

# K8s Node API
k8s_node_requests_total = Counter(
    "k8s_node_requests_total",
    "Total number of k8s node API requests",
    ["method", "endpoint", "status_code", "exception"]
)
k8s_node_requests_latency_seconds = Histogram(
    "k8s_node_requests_latency_seconds",
    "Latency of k8s node API requests in seconds",
    ["method", "endpoint", "status_code", "exception"]
)

# K8s Cluster Info API
k8s_cluster_info_requests_total = Counter(
    "k8s_cluster_info_requests_total",
    "Total number of k8s cluster info API requests",
    ["method", "endpoint", "status_code", "exception"]
)
k8s_cluster_info_requests_latency_seconds = Histogram(
    "k8s_cluster_info_requests_latency_seconds",
    "Latency of k8s cluster info API requests in seconds",
    ["method", "endpoint", "status_code", "exception"]
)

# K8s Get Token API
k8s_get_token_requests_total = Counter(
    "k8s_get_token_requests_total",
    "Total number of k8s get token API requests",
    ["method", "endpoint", "status_code", "exception"]
)
k8s_get_token_requests_latency_seconds = Histogram(
    "k8s_get_token_requests_latency_seconds",
    "Latency of k8s get token API requests in seconds",
    ["method", "endpoint", "status_code", "exception"]
)

# K8s Dashboard API
k8s_dashboard_requests_total = Counter(
    "k8s_dashboard_requests_total",
    "Total number of k8s dashboard API requests",
    ["method", "endpoint", "status_code", "exception"]
)
k8s_dashboard_requests_latency_seconds = Histogram(
    "k8s_dashboard_requests_latency_seconds",
    "Latency of k8s dashboard API requests in seconds",
    ["method", "endpoint", "status_code", "exception"]
)