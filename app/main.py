"""
FastAPI application entry point.
"""

import logging

import uvicorn
from fastapi import FastAPI
from app.routes import k8s_user_pod as k8s_user_pod_router

from app.routes.k8s_node import router as k8s_node_router
from app.routes.k8s_pod import router as k8s_pod_router
from app.routes.db_pod import router as db_pod_router
from app.routes.workload_request_decision import router as workload_router
from app.routes.k8s_node import router as node_router
from app.routes.tuning_parameters_api import router as tuning_parameters_router

app = FastAPI()

logging.basicConfig(level=logging.DEBUG)
app.include_router(workload_router, tags=["Workload Request"])
app.include_router(db_pod_router, tags=["DB Pods"])

app.include_router(k8s_pod_router, tags=["K8s Pods"])
app.include_router(k8s_node_router, tags=["K8s Nodes"])

app.include_router(k8s_user_pod_router.router, tags=["K8s User Pods"])

app.include_router(node_router, tags=["Nodes"])
app.include_router(tuning_parameters_router, tags=["Tuning Parameters"])

if __name__ == "__main__":
    print("starting main....")
    uvicorn.run(app, port=8083, host="0.0.0.0")
