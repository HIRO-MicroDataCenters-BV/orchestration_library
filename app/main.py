from fastapi import FastAPI, Depends

from app.routes import k8s_pod, k8s_node
from .routes import db_pod, workload_request, workload_request_decision
import logging

app = FastAPI()

logging.basicConfig(level=logging.DEBUG)
app.include_router(workload_request.router)
app.include_router(workload_request_decision.router)
app.include_router(db_pod.router)
app.include_router(k8s_pod.router)
app.include_router(k8s_node.router)
