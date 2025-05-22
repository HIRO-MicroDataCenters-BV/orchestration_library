"""
Schemas for the API requests and responses.
"""
from typing import Optional

from pydantic import BaseModel


class WorkloadRequestDecisionCreate(BaseModel):
    """
    Schema for creating a workload request decision.
    """

    workload_request_id: int
    node_name: str
    queue_name: str
    status: Optional[str] = "pending"


class WorkloadRequestDecisionUpdate(BaseModel):
    """
    Schema for updating a workload request decision.
    """

    status: str
    node_name: Optional[str] = None
    queue_name: Optional[str] = None
