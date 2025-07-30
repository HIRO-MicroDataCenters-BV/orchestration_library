"""
FastAPI application entry point.
"""

import logging

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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
    tuning_parameters_api,
    alerts_api,
    workload_action_api,
    workload_request_decision_api,
    wrokload_flow_api,
    container_power_metrics
)
from app.scheduler.metric_collector_scheduler import MetricCollectorScheduler

from app.utils.exception_handlers import init_exception_handlers

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust as needed for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.DEBUG)

app.include_router(k8s_pod.router, tags=["Kubernetes"])
app.include_router(k8s_pod_parent.router, tags=["Kubernetes"])
app.include_router(k8s_user_pod.router, tags=["Kubernetes"])
app.include_router(k8s_node.router, tags=["Kubernetes"])
app.include_router(k8s_cluster_info.router, tags=["Kubernetes"])
app.include_router(k8s_get_token_api.router, tags=["Kubernetes"])

app.include_router(tuning_parameters_api.router, tags=["Tuning Parameters"])
app.include_router(workload_request_decision_api.router, tags=["Workload Request Decision"])
app.include_router(alerts_api.router, tags=["Alerts API"])
app.include_router(workload_action_api.router, tags=["Workload Action"])
app.include_router(wrokload_flow_api.router, tags=["Workload Flow"])
app.include_router(container_power_metrics.router, tags=["Container Power Metrics"])

app.include_router(k8s_dashboard_api.router, tags=["Kubernetes Dashboard"])


init_exception_handlers(app)

metrics_scheduler = MetricCollectorScheduler(interval_seconds=10)

@app.on_event("startup")
async def start_scheduler():
    metrics_scheduler.start()

@app.on_event("shutdown")
async def stop_scheduler():
    metrics_scheduler.stop()


if __name__ == '__main__':
    uvicorn.run(app, port=8086, host='0.0.0.0')