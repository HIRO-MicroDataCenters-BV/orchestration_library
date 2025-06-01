"""
FastAPI application entry point.
"""

import logging

from fastapi import FastAPI
from app.api.k8s import (
    cluster_ui,
    k8s_pod,
    k8s_node,
    k8s_pod_parent,
    k8s_user_pod,
    k8s_cluster_info
)
from app.api import (
    pod,
    workload_request,
    workload_request_decision,
    node,
    tuning_parameters_api
)
from app.utils.exception_handlers import init_exception_handlers

app = FastAPI()

logging.basicConfig(level=logging.DEBUG)

app.include_router(k8s_pod.router, tags=["K8s Pod"])
app.include_router(k8s_pod_parent.router, tags=["K8s Pod Parent"])
app.include_router(k8s_user_pod.router, tags=["K8s User Pod"])
app.include_router(k8s_node.router, tags=["K8s Node"])
app.include_router(k8s_cluster_info.router, tags=["K8s Cluster Info"])
app.include_router(cluster_ui.router, tags=["K8s Cluster UI"])

app.include_router(workload_request.router, tags=["DB Workload Request"])
app.include_router(workload_request_decision.router, tags=["DB Workload Request Decision"])
app.include_router(pod.router, tags=["DB Pod"])
app.include_router(node.router, tags=["DB Node"])

app.include_router(tuning_parameters_api.router, tags=["Tuning Parameters"])


init_exception_handlers(app)
