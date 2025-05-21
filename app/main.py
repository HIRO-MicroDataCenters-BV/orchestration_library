"""
FastAPI application entry point.
"""

import logging

import uvicorn
from fastapi import FastAPI
from app.api.k8s import (k8s_pod, k8s_node, k8s_pod_parent, k8s_user_pod, k8s_cluster_info)
from app.api import (db_pod, workload_request, workload_request_decision, node, tuning_parameters_api)
from app.utils.exception_handlers import init_exception_handlers

app = FastAPI()

logging.basicConfig(level=logging.DEBUG)
app.include_router(workload_request.router)
app.include_router(workload_request_decision.router)
app.include_router(db_pod.router)
app.include_router(node.router)

app.include_router(k8s_pod.router)
app.include_router(k8s_pod_parent.router)
app.include_router(k8s_user_pod.router)
app.include_router(k8s_node.router)
app.include_router(k8s_cluster_info.router)

app.include_router(tuning_parameters_api.router, tags=["Tuning Parameters"])


init_exception_handlers(app)

if __name__ == "__main__":
    print("starting main....")
    uvicorn.run(app, port=8083, host="0.0.0.0")