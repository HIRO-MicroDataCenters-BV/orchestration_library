"""
Constants used across the application.
"""
from enum import Enum


WORKLOAD_ACTION_TYPE_ENUM = ("Bind", "Create", "Delete", "Move", "Swap")
WORKLOAD_ACTION_STATUS_ENUM = ("pending", "successful", "failed", "partial")
POD_PARENT_TYPE_ENUM = (
    "Deployment",
    "StatefulSet",
    "ReplicaSet",
    "Job",
    "DaemonSet",
    "CronJob",
)
WORKLOAD_REQUEST_DECISION_STATUS_ENUM = (
    "pending",
    "successful",
    "failed"
)

class WorkloadActionTypeEnum(str, Enum):
    """
    Enum for workload action types.
    """
    BIND = "Bind"
    CREATE = "Create"
    DELETE = "Delete"
    MOVE = "Move"
    SWAP = "Swap"

class WorkloadActionStatusEnum(str, Enum):
    """
    Enum for action statuses.
    """
    PENDING = "pending"
    SUCCESSFUL = "successful"
    FAILED = "failed"
    PARTIAL = "partial"

class PodParentTypeEnum(str, Enum):
    """Enum for pod parent types.
    """
    DEPLOYMENT = "Deployment"
    STATEFULSET = "StatefulSet"
    REPLICASET = "ReplicaSet"
    JOB = "Job"
    DAEMONSET = "DaemonSet"
    CRONJOB = "CronJob"
    OTHER = "Other"

class WorkloadRequestDecisionStatusEnum(str, Enum):
    """
    Enum for workload request decision statuses.
    """
    PENDING = "pending"
    SUCCESSFUL = "successful"
    FAILED = "failed"
