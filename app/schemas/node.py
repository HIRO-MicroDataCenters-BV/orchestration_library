"""
Schemas for the API requests and responses.
"""
from typing import Optional

from pydantic import BaseModel


class NodeCreate(BaseModel):
    """
    Schema for creating a node.
    """

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

    class Config:
        """
        Configuration class for Pydantic model.
        Provides settings for model behavior and validation.
        """
        orm_mode = True

        def get_orm_mode(self) -> bool:
            """
            Get the ORM mode setting.

            Returns:
                bool: True if ORM mode is enabled
            """
            return self.orm_mode

        def set_orm_mode(self, value: bool) -> None:
            """
            Set the ORM mode setting.

            Args:
                value (bool): New ORM mode value
            """
            self.orm_mode = value


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

    class Config:
        """
        Configuration class for Pydantic model.
        Provides settings for model behavior and validation.
        """
        orm_mode = True

        def get_orm_mode(self) -> bool:
            """
            Get the ORM mode setting.

            Returns:
                bool: True if ORM mode is enabled
            """
            return self.orm_mode

        def set_orm_mode(self, value: bool) -> None:
            """
            Set the ORM mode setting.

            Args:
                value (bool): New ORM mode value
            """
            self.orm_mode = value


class NodeResponse(BaseModel):
    """
    Response schema for a node object, typically used in API responses.
    """

    id: int
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
        Configuration class for Pydantic model.
        Provides settings for model behavior and validation.
        """
        orm_mode = True

        def get_orm_mode(self) -> bool:
            """
            Get the ORM mode setting.

            Returns:
                bool: True if ORM mode is enabled
            """
            return self.orm_mode

        def set_orm_mode(self, value: bool) -> None:
            """
            Set the ORM mode setting.

            Args:
                value (bool): New ORM mode value
            """
            self.orm_mode = value
