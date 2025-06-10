from pydantic import BaseModel, Field
from typing import Literal
from datetime import datetime
from enum import Enum

from sqlalchemy import (
    Column,
    TIMESTAMP,
    text,
)


class AlertType(str, Enum):
    """Enumeration for alert types matching database constraints."""
    ABNORMAL = "abnormal"
    NETWORK_ATTACK = "network-attack"
    OTHER = "other"


class AlertCreateRequest(BaseModel):
    """
    Schema for creating an alert request.
    Matches the PostgreSQL alerts table schema.
    """

    # id is SERIAL PRIMARY KEY - excluded from create request (auto-generated)
    alert_type: Literal["abnormal", "network-attack", "other"] = Field(
        ...,
        description="Type of alert (abnormal, network-attack, or other)",
        max_length=50
    )
    alert_description: str = Field(
        ...,
        description="Detailed description of the alert (TEXT field)"
    )
    pod_id: str = Field(
        ...,
        max_length=100,
        description="Kubernetes pod identifier"
    )
    node_id: str = Field(
        ...,
        max_length=100,
        description="Kubernetes node identifier"
    )


class AlertResponse(BaseModel):
    """
    Schema for alert response after creation.
    """

    id: int
    alert_type: str
    alert_description: str
    pod_id: str
    node_id: str
    datetime: datetime

    class Config:
        """Pydantic configuration."""
        from_attributes = True  # For SQLAlchemy ORM compatibility
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
