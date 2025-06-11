"""
Schemas for the API requests and responses.
"""

from pydantic import BaseModel
from uuid import UUID
from typing import Optional
from datetime import datetime


class PodRequestDecisionSchema(BaseModel):
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
