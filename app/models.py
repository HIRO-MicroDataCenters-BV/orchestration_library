"""
SQLAlchemy models for the orchestration library.
"""

# pylint: disable=too-few-public-methods

import uuid
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    TIMESTAMP,
    text,
    Float,
    Boolean,
)
from sqlalchemy.dialects.postgresql import UUID

from .database import Base


class WorkloadRequest(Base):
    """
    Model representing a workload request.
    """
    __tablename__ = "workload_request"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    namespace = Column(String(255), nullable=False)
    api_version = Column(String(50), nullable=False)
    kind = Column(String(50), nullable=False)
    current_scale = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

class WorkloadRequestDecision(Base):
    """
    Model representing a decision made for a workload request.
    """
    __tablename__ = "workload_request_decision"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workload_request_id = Column(
        Integer, ForeignKey("workload_request.id"), nullable=False
    )
    node_name = Column(String(255), nullable=False)
    queue_name = Column(String(255), nullable=False)
    status = Column(String(50), default="pending")
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

class Node(Base):
    """
    Model representing a node in the cluster.
    """
    __tablename__ = "node"

    id = Column(Integer, primary_key=True, index=True)
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

class Pod(Base):
    """
    Model representing a pod in the cluster.
    """
    __tablename__ = "pod"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    namespace = Column(String(255), nullable=False)
    demand_cpu = Column(Float, nullable=False)
    demand_memory = Column(Float, nullable=False)
    demand_slack_cpu = Column(Float)
    demand_slack_memory = Column(Float)
    is_elastic = Column(Boolean, nullable=False)
    assigned_node_id = Column(Integer, ForeignKey("node.id"))
    workload_request_id = Column(
        Integer, ForeignKey("workload_request.id"), nullable=False
    )
    status = Column(String(50), nullable=False)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
