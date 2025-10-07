"""
SQLAlchemy models for the Workload timings.
"""

from os import name
from uuid import uuid4
from sqlalchemy import (
    Column,
    Double,
    String,
    Boolean,
    TIMESTAMP,
    text,
    UUID,
    Enum as SAEnum,
)
from app.db.database import Base
from app.models.base_dict_mixin import BaseDictMixin
from app.utils.constants import (
    WorkloadTimingSchedulerEnum,
)


class WorkloadTiming(Base, BaseDictMixin):
    """
    Model representing the workload(pod) timings.
    """

    __tablename__ = "workload_timing"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False)
    pod_name = Column(String(255), nullable=False)
    namespace = Column(String(255), nullable=False)
    node_name = Column(String(255))
    scheduler_type = Column(
        SAEnum(
            WorkloadTimingSchedulerEnum,
            name="workload_timing_scheduler_enum",
            validate_strings=True
        ), nullable=False
    )
    pod_uid = Column(String(255), nullable=False)

    created_timestamp = Column(TIMESTAMP(timezone=True))
    scheduled_timestamp = Column(TIMESTAMP(timezone=True))
    ready_timestamp = Column(TIMESTAMP(timezone=True))
    deleted_timestamp = Column(TIMESTAMP(timezone=True))

    creation_to_scheduled_ms = Column(Double)
    scheduled_to_ready_ms = Column(Double)
    creation_to_ready_ms = Column(Double)
    total_lifecycle_ms = Column(Double)

    phase = Column(String(50))
    reason = Column(String)
    is_completed = Column(Boolean, default=False)
    recorded_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"))
