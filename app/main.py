from fastapi import FastAPI, Depends

from app.routes import k8s_pod
from .routes import workload_request, workload_request_decision, pod
import logging

app = FastAPI()

logging.basicConfig(level=logging.DEBUG)
app.include_router(workload_request.router)
app.include_router(workload_request_decision.router)
app.include_router(pod.router)
app.include_router(k8s_pod.router)
