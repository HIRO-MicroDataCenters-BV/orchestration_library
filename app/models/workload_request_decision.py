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
        Integer, ForeignKey("workload_request.id"), nullable=False
    )
    node_name = Column(String(255), nullable=False)
    queue_name = Column(String(255), nullable=False)
    status = Column(String(50), default="pending")
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    def to_dict(self):
        """
        Convert the model instance to a dictionary.
        """
        return {
            "id": str(self.id),
            "workload_request_id": self.workload_request_id,
            "node_name": self.node_name,
            "queue_name": self.queue_name,
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
            WorkloadRequestDecision: A new instance of the model.
        """
        return cls(
            workload_request_id=data.get("workload_request_id"),
            node_name=data.get("node_name"),
            queue_name=data.get("queue_name"),
            status=data.get("status", "pending"),
        )
