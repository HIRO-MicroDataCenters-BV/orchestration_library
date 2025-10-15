"""
SQLAlchemy models for Alerts.
This module defines the database models used for storing and retrieving Alerts.
"""

import ipaddress
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
from sqlalchemy.orm import validates

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

    # Pod Name - TEXT
    pod_name = Column(Text, nullable=True)

    # Node ID - UUID
    node_id = Column(UUID, nullable=True, index=True)  # Index for node queries

    # Node Name - TEXT
    node_name = Column(Text, nullable=True)

    # Additional fields for network-related alerts
    # Source IP - TEXT
    source_ip = Column(Text, nullable=True)

    # Source Port - INTEGER
    source_port = Column(Integer, nullable=True)

    # Destination IP - TEXT
    destination_ip = Column(Text, nullable=True)

    # Destination Port - INTEGER
    destination_port = Column(Integer, nullable=True)

    # Protocol - TEXT
    protocol = Column(Text, nullable=True)

    # Created At - TIMESTAMP with DEFAULT CURRENT_TIMESTAMP
    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        index=True,  # Index for time-based queries
    )

    @validates("source_ip", "destination_ip")
    def validate_ip(self, key, address):
        """
        Validate IP address format.
        """
        if address is not None:
            try:
                ipaddress.ip_address(address)
            except ValueError as exc:
                raise ValueError(f"{key} must be a valid IPv4 or IPv6 address") from exc
        return address

    @validates("source_port", "destination_port")
    def validate_port(self, key, port):
        """
        Validate port number.
        """
        if port is not None:
            if not 1 <= port <= 65535:
                raise ValueError(f"{key} must be between 1 and 65535")
        return port

    def __repr__(self) -> str:
        """
        String representation of the alert.

        Returns:
            str: String representation of the alert
        """
        return (
            f"<Alert(id={self.id}, "
            f"type={self.alert_type}, "
            f"type={self.alert_description}, "
            f"type={self.alert_model}, "
            f"pod={self.pod_id}, "
            f"node={self.node_id}, "
            f"node={self.source_ip}, "
            f"node={self.source_port}, "
            f"node={self.destination_ip}, "
            f"node={self.destination_port}, "
            f"node={self.protocol}, "
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
            f"from {self.alert_model} model"
            f"node {self.node_id} at {self.created_at} or"
            f"from ip {self.source_ip} with port {self.source_port} to "
            f"ip {self.destination_ip} with port {self.destination_port}  "
            f", with {self.protocol} and from {self.alert_model} model"
        )
