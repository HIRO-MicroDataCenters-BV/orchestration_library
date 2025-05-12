"""
FastAPI application entry point.
"""
import logging
from fastapi import FastAPI
from app.routes import k8s_pod, k8s_node, k8s_user_pod
from .routes import db_pod, workload_request, workload_request_decision

app = FastAPI()

logging.basicConfig(level=logging.DEBUG)
app.include_router(workload_request.router)
app.include_router(workload_request_decision.router)
app.include_router(db_pod.router)
app.include_router(k8s_pod.router)
app.include_router(k8s_user_pod.router)
app.include_router(k8s_node.router)
