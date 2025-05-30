"""
SQLAlchemy models for the orchestration library.
"""

from sqlalchemy import (
    Column,
    String,
    ForeignKey,
    TIMESTAMP,
    text,
    UUID
)

from app.db.database import Base
from app.models.base_dict_mixin import BaseDictMixin


class WorkloadRequestDecision(Base, BaseDictMixin):
    """
    Model representing a decision made for a workload request.
    """
    __tablename__ = "workload_request_decision"

    pod_id = Column(
        UUID(as_uuid=True),
        ForeignKey("pod.id"),
        primary_key=True,
        nullable=False
    )
    node_name = Column(String(255), nullable=False)
    queue_name = Column(String(255), nullable=False)
    status = Column(String(50), default="pending")
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
