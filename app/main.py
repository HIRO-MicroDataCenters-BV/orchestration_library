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
    k8s_cluster_info,
)
from app.api import pod_request_decision, tuning_parameters_api, alerts_api

from app.utils.exception_handlers import init_exception_handlers

app = FastAPI()

logging.basicConfig(level=logging.DEBUG)

app.include_router(k8s_pod.router, tags=["K8s Pod"])
app.include_router(k8s_pod_parent.router, tags=["K8s Pod Parent"])
app.include_router(k8s_user_pod.router, tags=["K8s User Pod"])
app.include_router(k8s_node.router, tags=["K8s Node"])
app.include_router(k8s_cluster_info.router, tags=["K8s Cluster Info"])
app.include_router(cluster_ui.router, tags=["K8s Cluster UI"])

app.include_router(tuning_parameters_api.router, tags=["Tuning Parameters"])
app.include_router(pod_request_decision.router, tags=["Pod Request Decision"])
app.include_router(alerts_api.router, tags=["Alerts API"])


init_exception_handlers(app)
