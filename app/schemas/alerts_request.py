"""
Pydantic models for Alert requests and responses.
This module defines the request and response models for the Alert API.
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class AlertType(str, Enum):
    """
    Enum for alert types.
    """

    ABNORMAL = "Abnormal"
    NETWORK_ATTACK = "Network-Attack"
    OTHER = "Other"

    def __repr__(self) -> str:
        """
        String representation of the alert type.

        Returns:
            str: String representation
        """
        return f"<AlertType.{self.name}>"

    def __str__(self) -> str:
        """
        Human-readable string representation of the alert type.

        Returns:
            str: Human-readable string representation
        """
        return self.value


class AlertCreateRequest(BaseModel):
    """
    Pydantic model for creating a new alert.
    """

    alert_type: AlertType = Field(
        ...,
        description="Type of alert",
        examples=["Abnormal", "Network-Attack", "Other"],
    )
    alert_model: str = Field(
        ...,
        description="Model used for the alert",
        min_length=1,
        max_length=1000,
        examples=["SampleAnomalyDetectionModel"],
    )
    alert_description: str = Field(
        ...,
        description="Description of the alert",
        min_length=1,
        max_length=1000,
        examples=["High CPU usage detected on pod"],
    )
    pod_id: Optional[UUID] = Field(
        ...,
        description="ID of the pod",
        examples=["123e4567-e89b-12d3-a456-426614174000"],
    )
    node_id: Optional[UUID] = Field(
        ...,
        description="ID of the node",
        examples=["123e4567-e89b-12d3-a456-426614174000"],
    )
    source_ip: Optional[str] = Field(
        None, description="Source IP address", examples=["192.168.1.1", "10.0.0.1"]
    )
    destination_ip: Optional[str] = Field(
        None, description="Destination IP address", examples=["192.168.1.2", "10.0.0.2"]
    )
    source_port: Optional[int] = Field(
        None, description="Source port number", ge=1, le=65535, examples=[80, 443]
    )
    destination_port: Optional[int] = Field(
        None, description="Destination port number", ge=1, le=65535, examples=[80, 443]
    )
    protocol: Optional[str] = Field(
        None,
        description="Network protocol used",
        examples=["TCP", "UDP", "ICMP"],
        min_length=1,
        max_length=10,
    )

    def __repr__(self) -> str:
        """
        String representation of the alert creation request.

        Returns:
            str: String representation
        """
        return (
            f"<AlertCreateRequest(type={self.alert_type}, "
            f"pod={self.pod_id}, node={self.node_id})>"
        )

    def __str__(self) -> str:
        """
        Human-readable string representation of the alert creation request.

        Returns:
            str: Human-readable string representation
        """
        return (
            f"AlertCreateRequest: {self.alert_type} on pod {self.pod_id} "
            f"node {self.node_id}"
        )


class AlertResponse(BaseModel):
    """
    Pydantic model for alert response.
    """

    id: int = Field(..., description="Unique identifier for the alert")
    alert_type: AlertType = Field(..., description="Type of alert")
    alert_model: str = Field(..., description="Model used for the alert")
    alert_description: str = Field(..., description="Description of the alert")
    pod_id: Optional[UUID] = Field(..., description="ID of the pod")
    node_id: Optional[UUID] = Field(..., description="ID of the node")
    source_ip: Optional[str] = Field(None, description="Source IP address")
    source_port: Optional[int] = Field(None, description="Source port number", ge=1, le=65535)
    destination_ip: Optional[str] = Field(None, description="Destination IP address")
    destination_port: Optional[int] = Field(
        None, description="Destination port number", ge=1, le=65535
    )
    protocol: Optional[str] = Field(
        None,
        description="Network protocol used",
        examples=["TCP", "UDP", "ICMP"],
        min_length=1,
        max_length=10,
    )
    created_at: datetime = Field(
        ..., description="Timestamp when the alert was created"
    )

    model_config = {'from_attributes': True}

    def __repr__(self) -> str:
        """
        String representation of the alert response.

        Returns:
            str: String representation
        """
        return (
            f"<AlertResponse(id={self.id}, type={self.alert_type}, model={self.alert_model}, "
            f"pod={self.pod_id}, node={self.node_id}, "
            f"created_at={self.created_at})>"
        )

    def __str__(self) -> str:
        """
        Human-readable string representation of the alert response.

        Returns:
            str: Human-readable string representation
        """
        return (
            f"AlertResponse {self.id}: {self.alert_type} on pod {self.pod_id} "
            f"node {self.node_id} at {self.created_at} by model {self.alert_model}"
        )
