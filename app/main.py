from fastapi import FastAPI, Depends
from .routes import workload_request, workload_request_decision

app = FastAPI()

app.include_router(workload_request.router)
app.include_router(workload_request_decision.router)

