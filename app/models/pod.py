"""
SQLAlchemy models for the orchestration library.
"""


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

from app.db.database import Base


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
