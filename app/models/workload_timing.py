"""
SQLAlchemy models for the Workload timings.
"""

from uuid import uuid4
from sqlalchemy import (
    Column,
    Double,
    String,
    Boolean,
    TIMESTAMP,
    text,
    UUID
)
from app.db.database import Base
from app.models.base_dict_mixin import BaseDictMixin
from app.utils.constants import (
    POD_PARENT_TYPE_ENUM,
    WORKLOAD_ACTION_TYPE_ENUM,
    WORKLOAD_REQUEST_DECISION_STATUS_ENUM,
)


class WorkloadTiming(Base, BaseDictMixin):
    """
    Model representing the pod timings.
    """

    __tablename__ = "workload_timing"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False)
    pod_name = Column(String(255), nullable=False)
    namespace = Column(String(255), nullable=False)
    node_name = Column(String(255))
    scheduler_type = Column(String(50))
    pod_uid = Column(String(255))

    created_timestamp = Column(TIMESTAMP(timezone=True, precision=6))
    scheduled_timestamp = Column(TIMESTAMP(timezone=True, precision=6))
    ready_timestamp = Column(TIMESTAMP(timezone=True, precision=6))
    deleted_timestamp = Column(TIMESTAMP(timezone=True, precision=6))

    creation_to_scheduled_ms = Column(Double)
    scheduled_to_ready_ms = Column(Double)
    creation_to_ready_ms = Column(Double)
    total_lifecycle_ms = Column(Double)

    phase = Column(String(50))
    reason = Column(String)
    is_completed = Column(Boolean, default=False)
    recorded_at = Column(
        TIMESTAMP(timezone=True), server_default=text("now()")
    )
