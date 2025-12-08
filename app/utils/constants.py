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
    "cronjob",
)
WORKLOAD_REQUEST_DECISION_STATUS_ENUM = ("pending", "succeeded", "failed")


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
    """Enum for pod parent types."""

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


class WorkloadTimingSchedulerEnum(str, Enum):
    """
    Enum for workload timing schedulers.
    """

    SCHEDULER_DEFAULT = "default-scheduler"
    SCHEDULER_RMS = "resource-management-service"


class AlertDescriptionEnum(str, Enum):
    """
    Enum for alert descriptions.
    """

    CPU_HOG = "CPU HOG"
    MEMORY_HOG = "MEMORY HOG"
    POD_FAILED = "FAILED"
    POD_LOG4SHELL = "LOG4SHELL"
    POD_HTTPSMUGGING = "HTTPSMUGGING"
    POD_REDIS_RCE = "REDIS RCE"
    POD_ATTACK_DETECTED = "ATTACK DETECTED"


CPU_RESOURCE_UPDATE_ALERTS = {
    AlertDescriptionEnum.CPU_HOG.value.lower(),
}

MEMORY_RESOURCE_UPDATE_ALERTS = {
    AlertDescriptionEnum.MEMORY_HOG.value.lower(),
}

POD_REDEPLOY_ALERTS = {
    AlertDescriptionEnum.POD_FAILED.value.lower(),
    AlertDescriptionEnum.POD_LOG4SHELL.value.lower(),
    AlertDescriptionEnum.POD_HTTPSMUGGING.value.lower(),
    AlertDescriptionEnum.POD_REDIS_RCE.value.lower(),
    AlertDescriptionEnum.POD_ATTACK_DETECTED.value.lower(),
}
