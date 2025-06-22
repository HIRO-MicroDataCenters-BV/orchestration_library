"""
FastAPI application entry point.
"""

import logging

from fastapi import FastAPI
from app.api.k8s import (
    k8s_get_token_api,
    k8s_pod,
    k8s_node,
    k8s_pod_parent,
    k8s_user_pod,
    k8s_cluster_info,
)
from app.api import dummy_aces_ui_api, pod_request_decision, tuning_parameters_api, alerts_api

from app.utils.exception_handlers import init_exception_handlers

app = FastAPI()

logging.basicConfig(level=logging.DEBUG)

app.include_router(k8s_pod.router, tags=["Kubernetes"])
app.include_router(k8s_pod_parent.router, tags=["Kubernetes"])
app.include_router(k8s_user_pod.router, tags=["Kubernetes"])
app.include_router(k8s_node.router, tags=["Kubernetes"])
app.include_router(k8s_cluster_info.router, tags=["Kubernetes"])
app.include_router(k8s_get_token_api.router, tags=["Kubernetes"])

app.include_router(tuning_parameters_api.router, tags=["Tuning Parameters"])
app.include_router(pod_request_decision.router, tags=["Pod Request Decision"])
app.include_router(alerts_api.router, tags=["Alerts API"])

app.include_router(dummy_aces_ui_api.router, tags=["Dummy ACES UI API"])


init_exception_handlers(app)
