"""
Schemas for the API requests and responses.
"""

from uuid import UUID
from typing import Optional
from datetime import datetime, timezone
from pydantic import BaseModel

from app.utils.constants import WorkloadTimingSchedulerEnum


class WorkloadTimingSchema(BaseModel):
    """
    Schema for workload timing.
    """

    id: UUID
    pod_name: str
    namespace: str
    node_name: Optional[str] = None
    scheduler_type: Optional[WorkloadTimingSchedulerEnum] = None
    pod_uid: Optional[str] = None

    created_timestamp: Optional[datetime] = None
    scheduled_timestamp: Optional[datetime] = None
    ready_timestamp: Optional[datetime] = None
    deleted_timestamp: Optional[datetime] = None

    creation_to_scheduled_ms: Optional[float] = None
    scheduled_to_ready_ms: Optional[float] = None
    creation_to_ready_ms: Optional[float] = None
    total_lifecycle_ms: Optional[float] = None

    phase: Optional[str] = None
    reason: Optional[str] = None
    is_completed: Optional[bool] = False
    recorded_at: Optional[datetime] = None

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


class WorkloadTimingCreate(BaseModel):
    """
    Schema for creating a workload timing.
    """

    id: UUID
    pod_name: str
    namespace: str
    node_name: str
    scheduler_type: WorkloadTimingSchedulerEnum
    pod_uid: str

    created_timestamp: Optional[datetime] = None
    scheduled_timestamp: Optional[datetime] = None
    ready_timestamp: Optional[datetime] = None
    deleted_timestamp: Optional[datetime] = None

    # The following fields are calculated from the timestamps
    # above and are not required in the create request:
    # - creation_to_scheduled_ms
    # - scheduled_to_ready_ms
    # - creation_to_ready_ms
    # - total_lifecycle_ms

    phase: Optional[str] = None
    reason: Optional[str] = None
    is_completed: Optional[bool] = False
    recorded_at: Optional[datetime] = datetime.now(timezone.utc)

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

class WorkloadTimingUpdate(BaseModel):
    """
    Schema for updating a workload timing.
    """

    created_timestamp: Optional[datetime] = None
    scheduled_timestamp: Optional[datetime] = None
    ready_timestamp: Optional[datetime] = None
    deleted_timestamp: Optional[datetime] = None

    # The following fields are calculated from the timestamps
    # above and are not required in the update request:
    # - creation_to_scheduled_ms
    # - scheduled_to_ready_ms
    # - creation_to_ready_ms
    # - total_lifecycle_ms

    phase: Optional[str] = None
    reason: Optional[str] = None
    is_completed: Optional[bool] = False
    recorded_at: Optional[datetime] = datetime.now(timezone.utc)

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
