"""
SQLAlchemy models for Alerts.
This module defines the database models used for storing and retrieving Alerts.
"""

from sqlalchemy import (
    TIMESTAMP,
    Column,
    Integer,
    String,
    Text,
    CheckConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID

from app.db.database import Base
from app.models.base_dict_mixin import BaseDictMixin


class Alert(Base, BaseDictMixin):
    """
    SQLAlchemy model for alerts table.
    Matches the PostgreSQL schema exactly.
    """

    __tablename__ = "alerts"

    # Primary Key - SERIAL
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Alert Type - VARCHAR(50) with CHECK constraint
    alert_type = Column(
        String(50),
        CheckConstraint("alert_type IN ('Abnormal', 'Network-Attack', 'Other')"),
        nullable=False,
        index=True,  # Add index for faster queries by type
    )

    alert_model = Column(Text, nullable=False)

    # Alert Description - TEXT
    alert_description = Column(Text, nullable=False)

    # Pod ID - UUID
    pod_id = Column(UUID, nullable=True, index=True)  # Index for pod queries

    # Node ID - UUID
    node_id = Column(UUID, nullable=True, index=True)  # Index for node queries

    source_ip = Column(Text, nullable=True)

    source_port = Column(Text, nullable=True)

    destination_ip = Column(Text, nullable=True)

    destination_port = Column(Text, nullable=True)

    protocol = Column(Text, nullable=True)

    # Created At - TIMESTAMP with DEFAULT CURRENT_TIMESTAMP
    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        index=True,  # Index for time-based queries
    )

    def __repr__(self) -> str:
        """
        String representation of the alert.

        Returns:
            str: String representation of the alert
        """
        return (
            f"<Alert(id={self.id}, "
            f"type={self.alert_type}, "
            f"pod={self.pod_id}, "
            f"node={self.node_id}, "
            f"node={self.source_ip}, "
            f"node={self.source_port}, "
            f"node={self.destination_ip}, "
            f"node={self.destination_port}, "
            f"created_at={self.created_at})>"
        )

    def __str__(self) -> str:
        """
        Human-readable string representation of the alert.

        Returns:
            str: Human-readable string representation
        """
        return (
            f"Alert {self.id}: {self.alert_type} on pod {self.pod_id} "
            f"node {self.node_id} at {self.created_at}"
        )
