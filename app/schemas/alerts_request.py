"""
Pydantic models for Alert requests and responses.
This module defines the request and response models for the Alert API.
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class AlertType(str, Enum):
    """
    Enum for alert types.
    """
    ABNORMAL = "abnormal"
    NETWORK_ATTACK = "network-attack"
    OTHER = "other"


class AlertCreateRequest(BaseModel):
    """
    Pydantic model for creating a new alert.
    """
    alert_type: AlertType = Field(
        ...,
        description="Type of alert",
        examples=["abnormal", "network-attack", "other"]
    )
    alert_description: str = Field(
        ...,
        description="Description of the alert",
        min_length=1,
        max_length=1000,
        examples=["High CPU usage detected on pod"]
    )
    pod_id: str = Field(
        ...,
        description="ID of the pod",
        min_length=1,
        max_length=100,
        examples=["pod-123"]
    )
    node_id: str = Field(
        ...,
        description="ID of the node",
        min_length=1,
        max_length=100,
        examples=["node-456"]
    )


class AlertResponse(BaseModel):
    """
    Pydantic model for alert response.
    """
    id: int = Field(..., description="Unique identifier for the alert")
    alert_type: AlertType = Field(..., description="Type of alert")
    alert_description: str = Field(..., description="Description of the alert")
    pod_id: str = Field(..., description="ID of the pod")
    node_id: str = Field(..., description="ID of the node")
    datetime: datetime = Field(..., description="Timestamp of the alert")

    class Config:
        """
        Pydantic model configuration.
        """
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
