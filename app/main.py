from fastapi import FastAPI, Depends
from .routes import workload_request, workload_request_decision, pod, node
import logging

app = FastAPI()

logging.basicConfig(level=logging.DEBUG)
app.include_router(workload_request.router)
app.include_router(workload_request_decision.router)
app.include_router(pod.router)
app.include_router(node.router)
