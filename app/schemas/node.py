"""
Schemas for the API requests and responses.
"""
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class NodeCreate(BaseModel):
    """
    Schema for creating a node.
    """
    id: UUID
    name: str
    status: Optional[str] = "active"
    cpu_capacity: float
    memory_capacity: float
    current_cpu_assignment: Optional[float] = None
    current_memory_assignment: Optional[float] = None
    current_cpu_utilization: Optional[float] = None
    current_memory_utilization: Optional[float] = None
    ip_address: Optional[str] = None
    location: Optional[str] = None


class NodeUpdate(BaseModel):
    """
    Schema for updating node information.
    """

    name: Optional[str] = None
    status: Optional[str] = None
    cpu_capacity: Optional[float] = None
    memory_capacity: Optional[float] = None
    current_cpu_assignment: Optional[float] = None
    current_memory_assignment: Optional[float] = None
    current_cpu_utilization: Optional[float] = None
    current_memory_utilization: Optional[float] = None
    ip_address: Optional[str] = None
    location: Optional[str] = None


class NodeResponse(BaseModel):
    """
    Response schema for a node object, typically used in API responses.
    """

    id: UUID
    name: str
    status: Optional[str]
    cpu_capacity: float
    memory_capacity: float
    current_cpu_assignment: Optional[float]
    current_memory_assignment: Optional[float]
    current_cpu_utilization: Optional[float]
    current_memory_utilization: Optional[float]
    ip_address: Optional[str]
    location: Optional[str]

    class Config:
        """
        config class
        """

        orm_mode = True

        def is_orm_mode(self):
            """
            Check if the model is in ORM mode.
            """
            return self.orm_mode
        def to_dict(self):
            """
            Convert the model instance to a dictionary.
            """
            return {"orm_mode": self.orm_mode}
