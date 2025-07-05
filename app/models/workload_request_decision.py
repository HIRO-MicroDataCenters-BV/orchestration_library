"""
SQLAlchemy models for the orchestration library.
"""

from uuid import uuid4
from sqlalchemy import (
    Column,
    String,
    Boolean,
    Float,
    TIMESTAMP,
    text,
    UUID,
    Enum as SAEnum,
)
from app.db.database import Base
from app.models.base_dict_mixin import BaseDictMixin
from app.utils.constants import POD_PARENT_TYPE_ENUM


class WorkloadRequestDecision(Base, BaseDictMixin):
    """
    Model representing the pod placement decision.
    """

    __tablename__ = "workload_request_decision"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False)
    pod_id = Column(UUID(as_uuid=True), nullable=False)
    pod_name = Column(String(255), nullable=False)
    namespace = Column(String(255), nullable=False)
    node_id = Column(UUID(as_uuid=True), nullable=False)
    node_name = Column(String(255), nullable=False)
    is_elastic = Column(Boolean, nullable=False)
    queue_name = Column(String(255), nullable=False)
    demand_cpu = Column(Float, nullable=False)
    demand_memory = Column(Float, nullable=False)
    demand_slack_cpu = Column(Float)
    demand_slack_memory = Column(Float)
    is_decision_status = Column(Boolean, nullable=False)
    pod_parent_id = Column(UUID(as_uuid=True), nullable=False)
    pod_parent_kind = Column(
        SAEnum(*POD_PARENT_TYPE_ENUM, name="pod_parent_type_enum"), nullable=False
    )
    created_at = Column(
        TIMESTAMP(timezone=True), server_default=text("CURRENT_TIMESTAMP"), index=True
    )
    deleted_at = Column(TIMESTAMP(timezone=True), nullable=True)
