"""
Pydantic models for Alert requests and responses.
This module defines the request and response models for the Alert API.
"""

from datetime import datetime
from enum import Enum
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
        examples=["Abnormal", "Network-Attack", "Other"]
    )
    alert_model: str = Field(
        ...,
        description="Model used for the alert",
        min_length=1,
        max_length=1000,
        examples=["SampleAnomalyDetectionModel"]
    )
    alert_description: str = Field(
        ...,
        description="Description of the alert",
        min_length=1,
        max_length=1000,
        examples=["High CPU usage detected on pod"]
    )
    pod_id: UUID = Field(
        ...,
        description="ID of the pod",
        examples=["123e4567-e89b-12d3-a456-426614174000"]
    )
    node_id: UUID = Field(
        ...,
        description="ID of the node",
        examples=["123e4567-e89b-12d3-a456-426614174000"]
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
            f"Create alert: {self.alert_type} on pod {self.pod_id} "
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
    pod_id: UUID = Field(..., description="ID of the pod")
    node_id: UUID = Field(..., description="ID of the node")
    created_at: datetime = Field(..., description="Timestamp when the alert was created")

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
            f"Alert {self.id}: {self.alert_type} on pod {self.pod_id} "
            f"node {self.node_id} at {self.created_at} by model {self.alert_model}"
        )

    class Config:
        """
        Pydantic model configuration.
        """
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

        def __repr__(self) -> str:
            """
            String representation of the config.

            Returns:
                str: String representation
            """
            return "<AlertResponse.Config>"

        def __str__(self) -> str:
            """
            Human-readable string representation of the config.

            Returns:
                str: Human-readable string representation
            """
            return "AlertResponse configuration"
