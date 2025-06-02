"""
Schemas for the API requests and responses.
"""
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class PodCreate(BaseModel):
    """
    Schema for creating a pod.
    """

    id: UUID
    name: str
    namespace: str
    demand_cpu: float
    demand_memory: float
    demand_slack_cpu: Optional[float] = None
    demand_slack_memory: Optional[float] = None
    is_elastic: bool
    assigned_node_id: Optional[UUID] = None
    workload_request_id: UUID
    status: Optional[str] = "pending"


class PodUpdate(BaseModel):
    """
    Schema for updating a pod.
    """

    demand_cpu: Optional[float] = None
    demand_memory: Optional[float] = None
    demand_slack_cpu: Optional[float] = None
    demand_slack_memory: Optional[float] = None
    is_elastic: Optional[bool] = None
    assigned_node_id: Optional[UUID] = None
    workload_request_id: Optional[UUID] = None
    status: Optional[str] = None
    queue_name: Optional[str] = None
