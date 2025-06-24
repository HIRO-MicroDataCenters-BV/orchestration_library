"""
Schemas for the API requests and responses.
"""

from uuid import UUID
from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class WorkloadDecisionSchema(BaseModel):
    """
    Schema for pod request decision.
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


class WorkloadDecisionUpdate(BaseModel):
    """
    Schema for pod request update decision.
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


class WorkloadDecisionCreate(BaseModel):
    """
    Schema for creating a pod request decision.
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
