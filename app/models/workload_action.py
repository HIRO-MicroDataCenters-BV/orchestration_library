"""
SQLAlchemy models for the orchestration library.
"""

from uuid import uuid4
from sqlalchemy import Column, String, TIMESTAMP, text, UUID, Enum
from app.db.database import Base
from app.models.base_dict_mixin import BaseDictMixin
from app.utils.constants import (
    WORKLOAD_ACTION_TYPE_ENUM,
    ACTION_STATUS_ENUM,
    POD_PARENT_TYPE_ENUM,
)


class WorkloadAction(Base, BaseDictMixin):
    """
    Model representing a workload action in the orchestration library.
    """

    __tablename__ = "workload_action"

    action_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        nullable=False,
        unique=True,
        index=True,
        doc="Request identifier",
    )

    action_type = Column(
        Enum(*WORKLOAD_ACTION_TYPE_ENUM, name="workload_action_type_enum"),
        nullable=False,
        doc="Type of the action within the request",
    )

    action_status = Column(
        Enum(*ACTION_STATUS_ENUM, name="action_status_enum"),
        nullable=True,
        doc="Status of the action",
    )
    action_start_time = Column(
        TIMESTAMP(timezone=True), nullable=True, doc="Start time of the action"
    )
    action_end_time = Column(
        TIMESTAMP(timezone=True), nullable=True, doc="End time of the action"
    )
    action_reason = Column(String, nullable=True, doc="Reason for the action")

    pod_parent_name = Column(
        String, nullable=True, doc="Name of the pod's parent resource"
    )
    pod_parent_type = Column(
        Enum(*POD_PARENT_TYPE_ENUM, name="pod_parent_type_enum"),
        nullable=True,
        doc="Type of the pod's parent resource",
    )
    pod_parent_uid = Column(
        UUID(as_uuid=True), nullable=True, doc="UID of the pod's parent resource"
    )

    created_pod_name = Column(String, nullable=True, doc="Name of the created pod")
    created_pod_namespace = Column(
        String, nullable=True, doc="Namespace of the created pod"
    )
    created_node_name = Column(
        String, nullable=True, doc="Node name where the pod was created"
    )

    deleted_pod_name = Column(String, nullable=True, doc="Name of the deleted pod")
    deleted_pod_namespace = Column(
        String, nullable=True, doc="Namespace of the deleted pod"
    )
    deleted_node_name = Column(
        String, nullable=True, doc="Node name where the pod was deleted"
    )

    bound_pod_name = Column(String, nullable=True, doc="Name of the bound pod")
    bound_pod_namespace = Column(
        String, nullable=True, doc="Namespace of the bound pod"
    )
    bound_node_name = Column(
        String, nullable=True, doc="Node name where the pod was bound"
    )

    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
        doc="Timestamp of record creation",
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=text("CURRENT_TIMESTAMP"),
        nullable=False,
        doc="Timestamp of last record update",
    )
