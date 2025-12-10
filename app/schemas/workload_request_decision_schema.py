"""
Schemas for the API requests and responses.
"""

from uuid import UUID
from typing import Optional
from datetime import datetime
from pydantic import BaseModel

from app.utils.constants import (
    PodParentTypeEnum,
    WorkloadActionTypeEnum,
)
from app.utils.constants import WorkloadRequestDecisionStatusEnum


# pylint: disable=too-few-public-methods
class DemandFields:
    """
    Schema for demand-related fields.
    """

    is_elastic: Optional[bool] = None
    queue_name: Optional[str] = None
    demand_cpu: Optional[float] = None
    demand_memory: Optional[float] = None
    demand_slack_cpu: Optional[float] = None
    demand_slack_memory: Optional[float] = None


class WorkloadRequestDecisionSchema(DemandFields, BaseModel):
    """
    Schema for workload decision.
    """

    id: UUID
    pod_id: UUID
    pod_name: str
    namespace: str
    node_id: UUID
    node_name: str
    action_type: WorkloadActionTypeEnum
    decision_status: WorkloadRequestDecisionStatusEnum
    pod_parent_id: Optional[UUID] = None
    pod_parent_name: Optional[str] = None
    pod_parent_kind: Optional[PodParentTypeEnum] = None
    decision_start_time: Optional[datetime] = None
    decision_end_time: Optional[datetime] = None
    created_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

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


class WorkloadRequestDecisionFilter(DemandFields, BaseModel):
    """
    Schema for workload decision filtering.
    """

    pod_name: Optional[str] = None
    namespace: Optional[str] = None
    node_id: Optional[UUID] = None
    node_name: Optional[str] = None
    action_type: Optional[WorkloadActionTypeEnum] = None
    decision_status: Optional[WorkloadRequestDecisionStatusEnum] = None
    pod_parent_id: Optional[UUID] = None
    pod_parent_name: Optional[str] = None
    pod_parent_kind: Optional[PodParentTypeEnum] = None
    decision_start_time: Optional[datetime] = None
    decision_end_time: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

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


class WorkloadRequestDecisionUpdate(DemandFields, BaseModel):
    """
    Schema for workload update decision.
    """

    pod_name: Optional[str] = None
    namespace: Optional[str] = None
    node_id: Optional[UUID] = None
    node_name: Optional[str] = None
    action_type: Optional[WorkloadActionTypeEnum] = None
    decision_status: Optional[WorkloadRequestDecisionStatusEnum] = None
    pod_parent_id: Optional[UUID] = None
    pod_parent_name: Optional[str] = None
    pod_parent_kind: Optional[PodParentTypeEnum] = None
    decision_start_time: Optional[datetime] = None
    decision_end_time: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

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


class WorkloadRequestDecisionStatusUpdate(BaseModel):
    """
    Schema for updating a workload request decision status.
    """

    pod_name: str
    namespace: str
    node_name: str
    action_type: WorkloadActionTypeEnum
    decision_status: WorkloadRequestDecisionStatusEnum = WorkloadRequestDecisionStatusEnum.SUCCEEDED

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


class WorkloadRequestDecisionCreate(DemandFields, BaseModel):
    """
    Schema for creating a workload decision.
    """

    pod_id: UUID
    pod_name: str
    namespace: str
    node_id: UUID
    node_name: str
    action_type: WorkloadActionTypeEnum
    decision_status: WorkloadRequestDecisionStatusEnum
    pod_parent_id: Optional[UUID] = None
    pod_parent_name: Optional[str] = None
    pod_parent_kind: Optional[PodParentTypeEnum] = None
    decision_start_time: Optional[datetime] = None
    decision_end_time: Optional[datetime] = None
    created_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

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
