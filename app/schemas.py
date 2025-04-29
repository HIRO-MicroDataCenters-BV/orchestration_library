from pydantic import BaseModel
from typing import Optional
from datetime import datetime


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


class WorkloadRequestDecisionUpdate(BaseModel):
    status: str
    node_name: Optional[str] = None
    queue_name: Optional[str] = None    

class PodCreate(BaseModel):
    name: str
    namespace: str
    demand_cpu: float
    demand_memory: float
    demand_slack_cpu: Optional[float] = None
    demand_slack_memory: Optional[float] = None
    is_elastic: bool
    assigned_node_id: Optional[int] = None
    status: Optional[str] = "pending"

class PodUpdate(BaseModel):
    name: Optional[str] = None
    namespace: Optional[str] = None
    demand_cpu: Optional[float] = None
    demand_memory: Optional[float] = None
    demand_slack_cpu: Optional[float] = None
    demand_slack_memory: Optional[float] = None
    is_elastic: Optional[bool] = None
    assigned_node_id: Optional[int] = None
    status: Optional[str] = None
    queue_name: Optional[str] = None


class WorkloadRequestUpdate(BaseModel):
    name: Optional[str] = None
    namespace: Optional[str] = None
    api_version: Optional[str] = None
    kind: Optional[str] = None
    current_scale: Optional[int] = None


class WorkloadRequestResponse(BaseModel):
    id: int
    name: str
    namespace: str
    api_version: str
    kind: str
    current_scale: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
