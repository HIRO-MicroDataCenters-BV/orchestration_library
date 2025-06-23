"""
Constants used across the application.
"""
WORKLOAD_ACTION_TYPE_ENUM = ("Bind", "Create", "Delete", "Move", "Swap")
ACTION_STATUS_ENUM = ("pending", "successful", "failed", "partial")
POD_PARENT_TYPE_ENUM = (
    "Deployment",
    "StatefulSet",
    "ReplicaSet",
    "Job",
    "DaemonSet",
    "CronJob",
)
