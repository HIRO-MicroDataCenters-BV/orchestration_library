"""
Schema for Placement Decision
"""
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# --------------------
# Input Schema
# --------------------
class PlacementDecisionID(BaseModel):
    """
    Schema for Placement Decision ID
    """
    name: str
    namespace: str

class PlacementDecisionField(BaseModel):
    """
    Schema for Placement Decision Field
    """
    placement: List[str]
    reason: str


class PlacementDecisionCreate(BaseModel):
    """
    Schema for creating a Placement Decision
    """
    id: PlacementDecisionID
    timestamp: Optional[datetime] = None
    spec: Dict[str, Any] = Field(
        description="Arbitrary spec JSON (free-form). Contains resources list.",
        example={
            "resources": [
                {
                    "id": {"name": "name", "namespace": "ns"},
                    "type": "pod",
                    "replicas": 2,
                    "requests": {
                        "cpu": "1",
                        "ram": "3",
                        "nvidia/gpu": "1"
                    },
                    "limits": {
                        "cpu": "1",
                        "ram": "3",
                        "ephemeral-storage": "1g"
                    }
                },
                {
                    "id": {"name": "name", "namespace": "ns"},
                    "type": "pvc",
                    "size": "1G",
                    "replicas": 2,
                    "storageClass": "default"
                }
            ]
        },
    )
    decision: PlacementDecisionField
    trace: Optional[str] = None


# --------------------
# Response on Save
# --------------------
class PlacementDecisionResponse(BaseModel):
    """
    Schema for responding with a Placement Decision
    """
    decision_id: Optional[uuid.UUID] = None
    status: str
    summary: Optional[str] = None
    details: Optional[str] = None


# --------------------
# Output Schema (DB → API)
# --------------------
# pylint: disable=too-few-public-methods
class PlacementDecisionOut(BaseModel):
    """
    Schema for outputting a Placement Decision
    """
    decision_id: uuid.UUID
    name: str
    namespace: str
    spec: dict  # JSONB → dict
    decision_placement_lst: List[str]  # ARRAY → list
    decision_reason: str
    trace: Optional[str] = None
    timestamp: datetime

    class Config:
        """
        Pydantic config for ORM mode
        """
        orm_mode = True
