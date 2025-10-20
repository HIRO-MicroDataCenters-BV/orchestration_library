"""
Schemas for workload decision and action flow.
"""

from uuid import UUID
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel

# Use the typed Enums already defined in constants for stricter validation
from app.schemas.workload_action_schema import PodActionPhaseFields
from app.schemas.workload_request_decision_schema import DemandFields
from app.utils.constants import (
    WorkloadActionTypeEnum,
    WorkloadActionStatusEnum,
    WorkloadRequestDecisionStatusEnum,
)

class FlowQueryParams(BaseModel):
    """
    Query parameters for workload decision action flow.
    """
    decision_id: Optional[UUID] = None
    action_id: Optional[UUID] = None
    pod_name: Optional[str] = None
    namespace: Optional[str] = None
    node_name: Optional[str] = None
    action_type: Optional[WorkloadActionTypeEnum] = None

class WorkloadDecisionActionFlowItem(PodActionPhaseFields, DemandFields, BaseModel):
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

    decision_pod_parent_id: Optional[UUID] = None
    decision_pod_parent_name: Optional[str] = None
    decision_pod_parent_kind: Optional[str] = None  # Could wrap with an Enum if needed

    action_pod_parent_name: Optional[str] = None
    action_pod_parent_type: Optional[str] = None
    action_pod_parent_uid: Optional[UUID] = None

    action_reason: Optional[str] = None
