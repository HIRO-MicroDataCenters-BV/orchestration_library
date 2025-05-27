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


class Pod(Base):
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

    def to_dict(self):
        """
        Convert the model instance to a dictionary.
        """
        return {
            "id": self.id,
            "name": self.name,
            "namespace": self.namespace,
            "demand_cpu": self.demand_cpu,
            "demand_memory": self.demand_memory,
            "demand_slack_cpu": self.demand_slack_cpu,
            "demand_slack_memory": self.demand_slack_memory,
            "is_elastic": self.is_elastic,
            "assigned_node_id": self.assigned_node_id,
            "workload_request_id": self.workload_request_id,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data):
        """
        Create a model instance from a dictionary.

        Args:
            data (dict): Dictionary containing model data.

        Returns:
            Pod: A new instance of the model.
        """
        return cls(
            name=data.get("name"),
            namespace=data.get("namespace"),
            demand_cpu=data.get("demand_cpu"),
            demand_memory=data.get("demand_memory"),
            demand_slack_cpu=data.get("demand_slack_cpu"),
            demand_slack_memory=data.get("demand_slack_memory"),
            is_elastic=data.get("is_elastic"),
            assigned_node_id=data.get("assigned_node_id"),
            workload_request_id=data.get("workload_request_id"),
            status=data.get("status", "pending"),
        )
