"""
Schema definitions for workload actions in a Kubernetes environment.

This module defines Pydantic schemas for creating, updating, and representing workload actions
such as binding, creating, deleting, moving, or swapping pods in a Kubernetes cluster.
"""

from uuid import UUID
from typing import Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field

from app.utils.constants import (
    PodParentTypeEnum,
    WorkloadActionStatusEnum,
    WorkloadActionTypeEnum,
)


class WorkloadAction(BaseModel):
    """
    Schema for workload action.
    """

    id: UUID
    action_type: WorkloadActionTypeEnum
    action_status: Optional[WorkloadActionStatusEnum] = None
    action_start_time: Optional[datetime] = None
    action_end_time: Optional[datetime] = None
    action_reason: Optional[str] = None

    pod_parent_name: Optional[str] = None
    pod_parent_type: Optional[PodParentTypeEnum] = None
    pod_parent_uid: Optional[UUID] = None

    created_pod_name: Optional[str] = None
    created_pod_namespace: Optional[str] = None
    created_node_name: Optional[str] = None

    deleted_pod_name: Optional[str] = None
    deleted_pod_namespace: Optional[str] = None
    deleted_node_name: Optional[str] = None

    bound_pod_name: Optional[str] = None
    bound_pod_namespace: Optional[str] = None
    bound_node_name: Optional[str] = None

    durationInSeconds: Optional[float] = None
    created_at: datetime = None
    updated_at: Optional[datetime] = None


class WorkloadActionCreate(BaseModel):
    """
    Schema for creating a workload action.
    """

    action_type: WorkloadActionTypeEnum = WorkloadActionTypeEnum.BIND
    action_status: WorkloadActionStatusEnum = WorkloadActionStatusEnum.PENDING
    action_start_time: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    action_end_time: Optional[datetime] = None
    action_reason: Optional[str] = None

    pod_parent_name: Optional[str] = None
    pod_parent_type: Optional[PodParentTypeEnum] = PodParentTypeEnum.DEPLOYMENT
    pod_parent_uid: Optional[UUID] = None

    created_pod_name: Optional[str] = None
    created_pod_namespace: Optional[str] = None
    created_node_name: Optional[str] = None

    deleted_pod_name: Optional[str] = None
    deleted_pod_namespace: Optional[str] = None
    deleted_node_name: Optional[str] = None

    bound_pod_name: Optional[str] = None
    bound_pod_namespace: Optional[str] = None
    bound_node_name: Optional[str] = None

    created_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class WorkloadActionUpdate(BaseModel):
    """
    Schema for updating a workload action.
    """

    action_type: Optional[WorkloadActionTypeEnum] = None
    action_status: Optional[WorkloadActionStatusEnum] = None
    action_start_time: Optional[datetime] = None
    action_end_time: Optional[datetime] = None
    action_reason: Optional[str] = None

    pod_parent_name: Optional[str] = None
    pod_parent_type: Optional[PodParentTypeEnum] = None
    pod_parent_uid: Optional[UUID] = None

    created_pod_name: Optional[str] = None
    created_pod_namespace: Optional[str] = None
    created_node_name: Optional[str] = None

    deleted_pod_name: Optional[str] = None
    deleted_pod_namespace: Optional[str] = None
    deleted_node_name: Optional[str] = None

    bound_pod_name: Optional[str] = None
    bound_pod_namespace: Optional[str] = None
    bound_node_name: Optional[str] = None

    updated_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))


class WorkloadActionFilters(BaseModel):
    """
    Schema for filtering workload actions.
    """

    action_type: Optional[WorkloadActionTypeEnum] = None
    action_status: Optional[WorkloadActionStatusEnum] = None
    action_start_time: Optional[datetime] = None
    action_end_time: Optional[datetime] = None
    action_reason: Optional[str] = None

    pod_parent_name: Optional[str] = None
    pod_parent_type: Optional[PodParentTypeEnum] = None
    pod_parent_uid: Optional[UUID] = None

    created_pod_name: Optional[str] = None
    created_pod_namespace: Optional[str] = None
    created_node_name: Optional[str] = None

    deleted_pod_name: Optional[str] = None
    deleted_pod_namespace: Optional[str] = None
    deleted_node_name: Optional[str] = None

    bound_pod_name: Optional[str] = None
    bound_pod_namespace: Optional[str] = None
    bound_node_name: Optional[str] = None
