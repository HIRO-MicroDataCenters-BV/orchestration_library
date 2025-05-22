"""
Schemas for the API requests and responses.
"""
from typing import Optional

from pydantic import BaseModel


class WorkloadRequestCreate(BaseModel):
    """
    Schema for creating a workload request.
    """

    name: str
    namespace: str
    api_version: str
    kind: str
    current_scale: int

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


class WorkloadRequestUpdate(BaseModel):
    """
    Schema for updating a workload request.
    """

    namespace: Optional[str] = None
    api_version: Optional[str] = None
    kind: Optional[str] = None
    current_scale: Optional[int] = None

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
