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
from sqlalchemy.orm import relationship
import uuid
from .database import Base


class WorkloadRequest(Base):
    __tablename__ = "workload_request"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    namespace = Column(String(255), nullable=False)
    api_version = Column(String(50), nullable=False)
    kind = Column(String(50), nullable=False)
    current_scale = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    # # Relationship to WorkloadRequestDecision
    # workload_request_decision = relationship("WorkloadRequestDecision", back_populates="workload_request")


class WorkloadRequestDecision(Base):
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

    # # Relationship to WorkloadRequest
    # workload_request = relationship("WorkloadRequest", back_populates="workload_request_decision")


class Node(Base):
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

    # # Relationship to Pod
    # pods = relationship("Pod", back_populates="node")


class Pod(Base):
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
    status = Column(String(50), nullable=False)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    # # Relationship to Node
    # node = relationship("Node", back_populates="pods")


class WorkloadRequestPod(Base):
    __tablename__ = "workload_request_pod"

    id = Column(Integer, primary_key=True, index=True)
    workload_request_id = Column(
        Integer, ForeignKey("workload_request.id"), nullable=False
    )
    pod_id = Column(Integer, ForeignKey("pod.id"), nullable=False)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    # Relationships
    # workload_request = relationship("WorkloadRequest", backref="workload_pods")
    # pod = relationship("Pod", backref="workload_requests")  # Assuming a Pod model exists
