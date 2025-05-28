"""
Schemas for the API requests and responses.
"""
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class WorkloadRequestCreate(BaseModel):
    """
    Schema for creating a workload request.
    """

    id: UUID
    name: str
    namespace: str
    api_version: str
    kind: str
    status: str
    current_scale: int

class WorkloadRequestUpdate(BaseModel):
    """
    Schema for updating a workload request.
    """

    namespace: Optional[str] = None
    api_version: Optional[str] = None
    kind: Optional[str] = None
    status: Optional[str] = None
    current_scale: Optional[int] = None
