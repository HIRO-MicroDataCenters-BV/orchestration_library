"""
Schemas for the API requests and responses.
"""

from uuid import UUID
from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class WorkloadRequestDecisionSchema(BaseModel):
    """
    Schema for workload decision.
    """
    id: UUID
    pod_id: UUID
    pod_name: str
    namespace: str
    node_id: UUID
    is_elastic: bool
    queue_name: str
    demand_cpu: float
    demand_memory: float
    demand_slack_cpu: Optional[float] = None
    demand_slack_memory: Optional[float] = None
    is_decision_status: bool
    pod_parent_id: UUID
    pod_parent_kind: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class WorkloadRequestDecisionUpdate(BaseModel):
    """
    Schema for workload update decision.
    """
    pod_name: Optional[str] = None
    namespace: Optional[str] = None
    node_id: Optional[UUID] = None
    is_elastic: Optional[bool] = None
    queue_name: Optional[str] = None
    demand_cpu: Optional[float] = None
    demand_memory: Optional[float] = None
    demand_slack_cpu: Optional[float] = None
    demand_slack_memory: Optional[float] = None
    is_decision_status: Optional[bool] = None
    pod_parent_id: Optional[UUID] = None
    pod_parent_kind: Optional[str] = None


class WorkloadRequestDecisionCreate(BaseModel):
    """
    Schema for creating a workload decision.
    """
    pod_id: UUID
    pod_name: str
    namespace: str
    node_id: UUID
    is_elastic: bool
    queue_name: str
    demand_cpu: float
    demand_memory: float
    demand_slack_cpu: Optional[float] = None
    demand_slack_memory: Optional[float] = None
    is_decision_status: bool
    pod_parent_id: UUID
    pod_parent_kind: str
