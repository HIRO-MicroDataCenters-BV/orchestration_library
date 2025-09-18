"""
Schemas for workload decision and action flow.
"""

from uuid import UUID
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel

# Use the typed Enums already defined in constants for stricter validation
from app.utils.constants import (
    WorkloadActionTypeEnum,
    WorkloadActionStatusEnum,
    WorkloadRequestDecisionStatusEnum,
)

class WorkloadDecisionActionFlowItem(BaseModel):
    """
    Schema for a single workload decision and action flow item.
    Matches columns from the workload_decision_action_flow view.
    """
    decision_id: UUID
    action_id: UUID
    action_type: WorkloadActionTypeEnum

    # Decision (d.*)
    decision_pod_name: Optional[str] = None
    decision_namespace: Optional[str] = None
    decision_node_name: Optional[str] = None

    # Created (action created_* set)
    created_pod_name: Optional[str] = None
    created_pod_namespace: Optional[str] = None
    created_node_name: Optional[str] = None

    # Deleted (action deleted_* set)
    deleted_pod_name: Optional[str] = None
    deleted_pod_namespace: Optional[str] = None
    deleted_node_name: Optional[str] = None

    # Bound (action bound_* set)
    bound_pod_name: Optional[str] = None
    bound_pod_namespace: Optional[str] = None
    bound_node_name: Optional[str] = None

    decision_status: Optional[WorkloadRequestDecisionStatusEnum] = None
    action_status: Optional[WorkloadActionStatusEnum] = None

    decision_start_time: Optional[datetime] = None
    decision_end_time: Optional[datetime] = None
    action_start_time: Optional[datetime] = None
    action_end_time: Optional[datetime] = None

    # INTERVAL columns -> timedelta for better typing
    decision_duration: Optional[timedelta] = None
    action_duration: Optional[timedelta] = None
    total_duration: Optional[timedelta] = None

    decision_created_at: Optional[datetime] = None
    decision_deleted_at: Optional[datetime] = None
    action_created_at: Optional[datetime] = None
    action_updated_at: Optional[datetime] = None

    is_elastic: Optional[bool] = None
    queue_name: Optional[str] = None

    demand_cpu: Optional[float] = None
    demand_memory: Optional[float] = None
    demand_slack_cpu: Optional[float] = None
    demand_slack_memory: Optional[float] = None

    decision_pod_parent_id: Optional[UUID] = None
    decision_pod_parent_name: Optional[str] = None
    decision_pod_parent_kind: Optional[str] = None  # Could wrap with an Enum if needed

    action_pod_parent_name: Optional[str] = None
    action_pod_parent_type: Optional[str] = None
    action_pod_parent_uid: Optional[UUID] = None

    action_reason: Optional[str] = None

    class Config:
        from_attributes = True  # Pydantic v2 replacement for