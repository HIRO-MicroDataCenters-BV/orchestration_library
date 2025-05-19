"""
FastAPI application entry point.
"""

import logging
from fastapi import FastAPI
from app.api.k8s import (k8s_pod, k8s_node, k8s_user_pod, k8s_cluster_info)
from app.api import (db_pod, workload_request, workload_request_decision, node)

app = FastAPI()

logging.basicConfig(level=logging.DEBUG)
app.include_router(workload_request.router)
app.include_router(workload_request_decision.router)
app.include_router(db_pod.router)
app.include_router(node.router)

app.include_router(k8s_pod.router)
app.include_router(k8s_user_pod.router)
app.include_router(k8s_node.router)
app.include_router(k8s_cluster_info.router)
