"""
SQLAlchemy models for the orchestration library.
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    TIMESTAMP,
    text,
    UUID
)

from app.db.database import Base


class WorkloadRequest(Base):
    """
    Model representing a workload request.
    """
    __tablename__ = "workload_request"

    id = Column(UUID(as_uuid=True), primary_key=True)
    name = Column(String(255), nullable=False)
    namespace = Column(String(255), nullable=False)
    api_version = Column(String(50), nullable=False)
    kind = Column(String(50), nullable=False)
    current_scale = Column(Integer, nullable=False)
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
            "api_version": self.api_version,
            "kind": self.kind,
            "current_scale": self.current_scale,
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
            WorkloadRequest: A new instance of the model.
        """
        return cls(
            name=data.get("name"),
            namespace=data.get("namespace"),
            api_version=data.get("api_version"),
            kind=data.get("kind"),
            current_scale=data.get("current_scale"),
        )
