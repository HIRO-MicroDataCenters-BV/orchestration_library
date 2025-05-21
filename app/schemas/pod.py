"""
Schemas for the API requests and responses.
"""
from typing import Optional

from pydantic import BaseModel


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
