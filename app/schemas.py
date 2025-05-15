"""
Schemas for the API requests and responses.
"""
from typing import Optional

from pydantic import BaseModel


class WorkloadRequestCreate(BaseModel):
    """
    Schema for creating a workload request.
    """

    name: str
    namespace: str
    api_version: str
    kind: str
    current_scale: int


class WorkloadRequestDecisionCreate(BaseModel):
    """
    Schema for creating a workload request decision.
    """

    workload_request_id: int
    node_name: str
    queue_name: str
    status: Optional[str] = "pending"


class WorkloadRequestDecisionUpdate(BaseModel):
    """
    Schema for updating a workload request decision.
    """

    status: str
    node_name: Optional[str] = None
    queue_name: Optional[str] = None


class PodCreate(BaseModel):
    """
    Schema for creating a pod.
    """

    name: str
    namespace: str
    demand_cpu: float
    demand_memory: float
    demand_slack_cpu: Optional[float] = None
    demand_slack_memory: Optional[float] = None
    is_elastic: bool
    assigned_node_id: Optional[int] = None
    workload_request_id: int
    status: Optional[str] = "pending"


class PodUpdate(BaseModel):
    """
    Schema for updating a pod.
    """

    name: Optional[str] = None
    namespace: Optional[str] = None
    demand_cpu: Optional[float] = None
    demand_memory: Optional[float] = None
    demand_slack_cpu: Optional[float] = None
    demand_slack_memory: Optional[float] = None
    is_elastic: Optional[bool] = None
    assigned_node_id: Optional[int] = None
    workload_request_id: Optional[int] = None
    status: Optional[str] = None
    queue_name: Optional[str] = None


class WorkloadRequestUpdate(BaseModel):
    """
    Schema for updating a workload request.
    """

    namespace: Optional[str] = None
    api_version: Optional[str] = None
    kind: Optional[str] = None
    current_scale: Optional[int] = None


class WorkloadRequestPodUpdate(BaseModel):
    """
    Schema for updating a workload request with pod information.
    """

    workload_request_id: Optional[int] = None
    pod_id: Optional[int] = None


class NodeCreate(BaseModel):
    name: str
    status: Optional[str] = "active"
    cpu_capacity: float
    memory_capacity: float
    current_cpu_assignment: Optional[float] = None
    current_memory_assignment: Optional[float] = None
    current_cpu_utilization: Optional[float] = None
    current_memory_utilization: Optional[float] = None


class NodeUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None
    cpu_capacity: Optional[float] = None
    memory_capacity: Optional[float] = None
    current_cpu_assignment: Optional[float] = None
    current_memory_assignment: Optional[float] = None
    current_cpu_utilization: Optional[float] = None
    current_memory_utilization: Optional[float] = None


class NodeResponse(BaseModel):
    id: int
    name: str
    status: Optional[str]
    cpu_capacity: float
    memory_capacity: float
    current_cpu_assignment: Optional[float]
    current_memory_assignment: Optional[float]
    current_cpu_utilization: Optional[float]
    current_memory_utilization: Optional[float]
    ip_address: str
    location: Optional[str]

    class Config:
        orm_mode = True
