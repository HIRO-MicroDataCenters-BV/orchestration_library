"""
Constants used across the application.
"""
from enum import Enum


K8S_IN_USE_NAMESPACE_REGEX = "^kube-.*$|^default$"

PLACEMENT_DECISION_STATUS_OK = "OK"
PLACEMENT_DECISION_STATUS_FAILURE = "FAILURE"

WORKLOAD_ACTION_TYPE_ENUM = ("bind", "create", "delete", "move", "swap_x", "swap_y")
WORKLOAD_ACTION_STATUS_ENUM = ("pending", "succeeded", "failed")
POD_PARENT_TYPE_ENUM = (
    "deployment",
    "statefulset",
    "replicaset",
    "job",
    "daemonset",
    "cronjob"
)
WORKLOAD_REQUEST_DECISION_STATUS_ENUM = (
    "pending",
    "succeeded",
    "failed"
)

class WorkloadActionTypeEnum(str, Enum):
    """
    Enum for workload action types.
    """
    BIND = "bind"
    CREATE = "create"
    DELETE = "delete"
    MOVE = "move"
    SWAP_X = "swap_x"
    SWAP_Y = "swap_y"

class WorkloadActionStatusEnum(str, Enum):
    """
    Enum for action statuses.
    """
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"

class PodParentTypeEnum(str, Enum):
    """Enum for pod parent types.
    """
    DEPLOYMENT = "deployment"
    STATEFULSET = "statefulset"
    REPLICASET = "replicaset"
    JOB = "job"
    DAEMONSET = "daemonset"
    CRONJOB = "cronjob"

class WorkloadRequestDecisionStatusEnum(str, Enum):
    """
    Enum for workload request decision statuses.
    """
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
