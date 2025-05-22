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


class WorkloadRequestDecisionUpdate(BaseModel):
    """
    Schema for updating a workload request decision.
    """

    status: str
    node_name: Optional[str] = None
    queue_name: Optional[str] = None

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
