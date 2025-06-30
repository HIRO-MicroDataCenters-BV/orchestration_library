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
    WORKLOAD_ACTION_TYPE_ENUM,
    ACTION_STATUS_ENUM,
    POD_PARENT_TYPE_ENUM,
)


class WorkloadAction(BaseModel):
    """
    Schema for workload action.
    """

    id: UUID = Field(..., description="Unique identifier for the request")
    action_type: str = Field(
        ...,
        description="Type of the action within the request",
        enum=WORKLOAD_ACTION_TYPE_ENUM,
    )
    action_status: Optional[str] = Field(
        None, description="Status of the action", enum=ACTION_STATUS_ENUM
    )
    action_start_time: Optional[datetime] = Field(
        None, description="Start time of the action"
    )
    action_end_time: Optional[datetime] = Field(
        None, description="End time of the action"
    )
    action_reason: Optional[str] = Field(None, description="Reason for the action")

    pod_parent_name: Optional[str] = Field(
        None, description="Name of the pod's parent resource"
    )
    pod_parent_type: Optional[str] = Field(
        None, description="Type of the pod's parent resource", enum=POD_PARENT_TYPE_ENUM
    )
    pod_parent_uid: Optional[UUID] = Field(
        None, description="UID of the pod's parent resource"
    )

    created_pod_name: Optional[str] = Field(None, description="Name of the created pod")
    created_pod_namespace: Optional[str] = Field(
        None, description="Namespace of the created pod"
    )
    created_node_name: Optional[str] = Field(
        None, description="Node name where the pod was created"
    )

    deleted_pod_name: Optional[str] = Field(None, description="Name of the deleted pod")
    deleted_pod_namespace: Optional[str] = Field(
        None, description="Namespace of the deleted pod"
    )
    deleted_node_name: Optional[str] = Field(
        None, description="Node name where the pod was deleted"
    )

    bound_pod_name: Optional[str] = Field(None, description="Name of the bound pod")
    bound_pod_namespace: Optional[str] = Field(
        None, description="Namespace of the bound pod"
    )
    bound_node_name: Optional[str] = Field(
        None, description="Node name where the pod was bound"
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when the action was created",
    )
    updated_at: Optional[datetime] = Field(
        None, description="Timestamp when the action was last updated"
    )


class WorkloadActionUpdate(BaseModel):
    """
    Schema for updating a workload action.
    """

    action_type: Optional[str] = Field(
        None,
        description="Type of the action within the request",
        enum=WORKLOAD_ACTION_TYPE_ENUM,
    )
    action_status: Optional[str] = Field(
        None, description="Status of the action", enum=ACTION_STATUS_ENUM
    )
    action_start_time: Optional[datetime] = Field(
        None, description="Start time of the action"
    )
    action_end_time: Optional[datetime] = Field(
        None, description="End time of the action"
    )
    action_reason: Optional[str] = Field(None, description="Reason for the action")

    pod_parent_name: Optional[str] = Field(
        None, description="Name of the pod's parent resource"
    )
    pod_parent_type: Optional[str] = Field(
        None, description="Type of the pod's parent resource", enum=POD_PARENT_TYPE_ENUM
    )
    pod_parent_uid: Optional[UUID] = Field(
        None, description="UID of the pod's parent resource"
    )

    created_pod_name: Optional[str] = Field(None, description="Name of the created pod")
    created_pod_namespace: Optional[str] = Field(
        None, description="Namespace of the created pod"
    )
    created_node_name: Optional[str] = Field(
        None, description="Node name where the pod was created"
    )

    deleted_pod_name: Optional[str] = Field(None, description="Name of the deleted pod")
    deleted_pod_namespace: Optional[str] = Field(
        None, description="Namespace of the deleted pod"
    )
    deleted_node_name: Optional[str] = Field(
        None, description="Node name where the pod was deleted"
    )

    bound_pod_name: Optional[str] = Field(None, description="Name of the bound pod")
    bound_pod_namespace: Optional[str] = Field(
        None, description="Namespace of the bound pod"
    )
    bound_node_name: Optional[str] = Field(
        None, description="Node name where the pod was bound"
    )

    updated_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when the action was last updated"
    )


class WorkloadActionCreate(BaseModel):
    """
    Schema for creating a workload action.
    """

    action_type: str = Field(
        ...,
        description="Type of the action within the request",
        enum=WORKLOAD_ACTION_TYPE_ENUM,
    )
    action_status: Optional[str] = Field(
        None, description="Status of the action", enum=ACTION_STATUS_ENUM
    )
    action_start_time: Optional[datetime] = Field(
        None, description="Start time of the action"
    )
    action_end_time: Optional[datetime] = Field(
        None, description="End time of the action"
    )
    action_reason: Optional[str] = Field(None, description="Reason for the action")

    pod_parent_name: Optional[str] = Field(
        None, description="Name of the pod's parent resource"
    )
    pod_parent_type: Optional[str] = Field(
        None, description="Type of the pod's parent resource", enum=POD_PARENT_TYPE_ENUM
    )
    pod_parent_uid: Optional[UUID] = Field(
        None, description="UID of the pod's parent resource"
    )

    created_pod_name: Optional[str] = Field(None, description="Name of the created pod")
    created_pod_namespace: Optional[str] = Field(
        None, description="Namespace of the created pod"
    )
    created_node_name: Optional[str] = Field(
        None, description="Node name where the pod was created"
    )

    deleted_pod_name: Optional[str] = Field(None, description="Name of the deleted pod")
    deleted_pod_namespace: Optional[str] = Field(
        None, description="Namespace of the deleted pod"
    )
    deleted_node_name: Optional[str] = Field(
        None, description="Node name where the pod was deleted"
    )

    bound_pod_name: Optional[str] = Field(None, description="Name of the bound pod")
    bound_pod_namespace: Optional[str] = Field(
        None, description="Namespace of the bound pod"
    )
    bound_node_name: Optional[str] = Field(
        None, description="Node name where the pod was bound"
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when the action was created",
    )
    updated_at: Optional[datetime] = Field(
        None, description="Timestamp when the action was last updated"
    )

class WorkloadActionFilters(BaseModel):
    """
    Schema for filtering workload actions.
    """

    action_type: Optional[str] = Field(
        None, description="Filter by action type", enum=WORKLOAD_ACTION_TYPE_ENUM
    )
    action_status: Optional[str] = Field(
        None, description="Filter by action status", enum=ACTION_STATUS_ENUM
    )
    start_time: Optional[datetime] = Field(
        None, description="Filter by start time"
    )
    end_time: Optional[datetime] = Field(
        None, description="Filter by end time"
    )
    action_reason: Optional[str] = Field(
        None, description="Filter by action reason"
    )
    pod_parent_name: Optional[str] = Field(
        None, description="Filter by pod parent name"
    )
    pod_parent_type: Optional[str] = Field(
        None, description="Filter by pod parent type", enum=POD_PARENT_TYPE_ENUM
    )
    pod_parent_uid: Optional[UUID] = Field(
        None, description="Filter by pod parent UID"
    )
    created_pod_name: Optional[str] = Field(
        None, description="Filter by created pod name"
    )
    created_pod_namespace: Optional[str] = Field(
        None, description="Filter by created pod namespace"
    )
    created_node_name: Optional[str] = Field(
        None, description="Filter by created node name"
    )
    deleted_pod_name: Optional[str] = Field(
        None, description="Filter by deleted pod name"
    )
    deleted_pod_namespace: Optional[str] = Field(
        None, description="Filter by deleted pod namespace"
    )
    deleted_node_name: Optional[str] = Field(
        None, description="Filter by deleted node name"
    )
    bound_pod_name: Optional[str] = Field(
        None, description="Filter by bound pod name"
    )
    bound_pod_namespace: Optional[str] = Field(
        None, description="Filter by bound pod namespace"
    )
    bound_node_name: Optional[str] = Field(
        None, description="Filter by bound node name"
    )
