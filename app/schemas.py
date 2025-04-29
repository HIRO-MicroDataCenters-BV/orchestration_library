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
