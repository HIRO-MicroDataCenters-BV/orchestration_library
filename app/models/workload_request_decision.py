"""
SQLAlchemy models for the orchestration library.
"""

# pylint: disable=too-few-public-methods

from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    TIMESTAMP,
    text,
    UUID
)

from app.db.database import Base


class WorkloadRequestDecision(Base):
    """
    Model representing a decision made for a workload request.
    """
    __tablename__ = "workload_request_decision"

    id = Column(UUID(as_uuid=True), primary_key=True)
    workload_request_id = Column(
        UUID(as_uuid=True), ForeignKey("workload_request.id"), nullable=False
    )
    node_name = Column(String(255), nullable=False)
    queue_name = Column(String(255), nullable=False)
    status = Column(String(50), default="pending")
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
