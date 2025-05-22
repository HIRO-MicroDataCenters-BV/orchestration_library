"""
SQLAlchemy models for the orchestration library.
"""


from sqlalchemy import (
    Column,
    Integer,
    String,
    TIMESTAMP,
    text,
    Float
)

from app.db.database import Base


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

    def to_dict(self):
        """
        Convert the model instance to a dictionary.
        """
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status,
            "cpu_capacity": self.cpu_capacity,
            "memory_capacity": self.memory_capacity,
            "current_cpu_assignment": self.current_cpu_assignment,
            "current_memory_assignment": self.current_memory_assignment,
            "current_cpu_utilization": self.current_cpu_utilization,
            "current_memory_utilization": self.current_memory_utilization,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "ip_address": self.ip_address,
            "location": self.location,
        }

    @classmethod
    def from_dict(cls, data):
        """
        Create a model instance from a dictionary.

        Args:
            data (dict): Dictionary containing model data.

        Returns:
            Node: A new instance of the model.
        """
        return cls(
            name=data.get("name"),
            status=data.get("status", "active"),
            cpu_capacity=data.get("cpu_capacity"),
            memory_capacity=data.get("memory_capacity"),
            current_cpu_assignment=data.get("current_cpu_assignment"),
            current_memory_assignment=data.get("current_memory_assignment"),
            current_cpu_utilization=data.get("current_cpu_utilization"),
            current_memory_utilization=data.get("current_memory_utilization"),
            ip_address=data.get("ip_address"),
            location=data.get("location"),
        )
