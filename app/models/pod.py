"""
SQLAlchemy models for the orchestration library.
"""


from sqlalchemy import (
    Column,
    String,
    ForeignKey,
    TIMESTAMP,
    text,
    Float,
    Boolean,
    UUID
)

from app.db.database import Base
from app.models.base_dict_mixin import BaseDictMixin


class Pod(Base, BaseDictMixin):
    """
    Model representing a pod in the cluster.
    """
    __tablename__ = "pod"

    id = Column(UUID(as_uuid=True), primary_key=True)
    name = Column(String(255), nullable=False)
    namespace = Column(String(255), nullable=False)
    demand_cpu = Column(Float, nullable=False)
    demand_memory = Column(Float, nullable=False)
    demand_slack_cpu = Column(Float)
    demand_slack_memory = Column(Float)
    is_elastic = Column(Boolean, nullable=False)
    assigned_node_id = Column(UUID(as_uuid=True), ForeignKey("node.id"))
    workload_request_id = Column(
        UUID(as_uuid=True), ForeignKey("workload_request.id"), nullable=False
    )
    status = Column(String(50), nullable=False)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
