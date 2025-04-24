from pydantic import BaseModel
from typing import Optional

class WorkloadRequestCreate(BaseModel):
    name: str
    namespace: str
    api_version: str
    kind: str
    current_scale: int

class WorkloadRequestDecisionCreate(BaseModel):
    workload_request_id: int
    node_name: str
    queue_name: str
    status: Optional[str] = "pending"
