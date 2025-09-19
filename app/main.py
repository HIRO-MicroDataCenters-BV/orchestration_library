"""
FastAPI application entry point.
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from app.api.k8s import (
    k8s_dashboard_api,
    k8s_get_token_api,
    k8s_pod,
    k8s_node,
    k8s_pod_parent,
    k8s_user_pod,
    k8s_cluster_info,
)
from app.api import (
    placement_decision_api,
    tuning_parameters_api,
    alerts_api,
    workload_action_api,
    workload_decision_action_flow_api,
    workload_request_decision_api
)
from app.logger.logging_config import setup_logging
from app.utils.exception_handlers import init_exception_handlers


app = FastAPI(title="Orchestration Library API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust as needed for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

setup_logging(log_file="orchestration_app.log", level=logging.INFO)
# logging.basicConfig(level=logging.DEBUG)

app.include_router(k8s_pod.router, tags=["Kubernetes"])
app.include_router(k8s_pod_parent.router, tags=["Kubernetes"])
app.include_router(k8s_user_pod.router, tags=["Kubernetes"])
app.include_router(k8s_node.router, tags=["Kubernetes"])
app.include_router(k8s_cluster_info.router, tags=["Kubernetes"])
app.include_router(k8s_get_token_api.router, tags=["Kubernetes"])
app.include_router(k8s_dashboard_api.router, tags=["Kubernetes Dashboard"])

app.include_router(tuning_parameters_api.router, tags=["Tuning Parameters"])
app.include_router(workload_request_decision_api.router, tags=["Workload Request Decision"])
app.include_router(alerts_api.router, tags=["Alerts API"])
app.include_router(workload_action_api.router, tags=["Workload Action"])
app.include_router(workload_decision_action_flow_api.router, tags=["Workload Decision Action Flow"])

app.include_router(placement_decision_api.router, tags=["Placement Decisions"])

init_exception_handlers(app)

# Instrumentation
Instrumentator().instrument(app).expose(app, endpoint="/metrics", tags=["Metrics"])
