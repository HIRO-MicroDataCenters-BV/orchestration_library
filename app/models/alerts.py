"""
SQLAlchemy models for Alerts.
This module defines the database models used for storing and retrieving Alerts.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, CheckConstraint
from sqlalchemy.sql import func

from app.db.database import Base


class Alert(Base):
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
        CheckConstraint("alert_type IN ('abnormal', 'network-attack', 'other')"),
        nullable=False,
        index=True  # Add index for faster queries by type
    )

    # Alert Description - TEXT
    alert_description = Column(Text, nullable=False)

    # Pod ID - VARCHAR(100)
    pod_id = Column(String(100), nullable=False, index=True)  # Index for pod queries

    # Node ID - VARCHAR(100)
    node_id = Column(String(100), nullable=False, index=True)  # Index for node queries

    # Datetime - TIMESTAMP with DEFAULT CURRENT_TIMESTAMP
    datetime = Column(
        DateTime(timezone=True),
        nullable=False,
        default=func.current_timestamp,
        server_default=func.current_timestamp,
        index=True  # Index for time-based queries
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
            f"datetime={self.datetime})>"
        )
