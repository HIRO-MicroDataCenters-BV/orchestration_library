"""
SQLAlchemy models for the orchestration library.
"""

# pylint: disable=too-few-public-methods

from sqlalchemy import (
    Column,
    String,
    TIMESTAMP,
    text,
    Float,
    UUID
)

from app.db.database import Base


class Node(Base):
    """
    Model representing a node in the cluster.
    """
    __tablename__ = "node"

    id = Column(UUID(as_uuid=True), primary_key=True)
    name = Column(String(255), nullable=False)
    status = Column(String(50), default="active")
    cpu_capacity = Column(Float, nullable=False)
    memory_capacity = Column(Float, nullable=False)
    current_cpu_assignment = Column(Float)
    current_memory_assignment = Column(Float)
    current_cpu_utilization = Column(Float)
    current_memory_utilization = Column(Float)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    ip_address = Column(String)
    location = Column(String)
