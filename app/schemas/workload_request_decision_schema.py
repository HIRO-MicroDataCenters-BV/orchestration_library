"""
Schemas for the API requests and responses.
"""

from uuid import UUID
from typing import Optional
from datetime import datetime, timezone
from pydantic import BaseModel

from app.utils.constants import PodParentTypeEnum
from app.utils.constants import WorkloadRequestDecisionStatusEnum


class WorkloadRequestDecisionSchema(BaseModel):
    """
    Schema for workload decision.
    """

    id: UUID
    pod_id: UUID
    pod_name: str
    namespace: str
    node_id: UUID
    node_name: str
    is_elastic: bool
    queue_name: str
    demand_cpu: float
    demand_memory: float
    demand_slack_cpu: Optional[float] = None
    demand_slack_memory: Optional[float] = None
    decision_status: WorkloadRequestDecisionStatusEnum
    pod_parent_id: UUID
    pod_parent_name: str
    pod_parent_kind: PodParentTypeEnum
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


class WorkloadRequestDecisionUpdate(BaseModel):
    """
    Schema for workload update decision.
    """

    pod_name: Optional[str] = None
    namespace: Optional[str] = None
    node_id: Optional[UUID] = None
    node_name: Optional[str] = None
    is_elastic: Optional[bool] = None
    queue_name: Optional[str] = None
    demand_cpu: Optional[float] = None
    demand_memory: Optional[float] = None
    demand_slack_cpu: Optional[float] = None
    demand_slack_memory: Optional[float] = None
    decision_status: Optional[WorkloadRequestDecisionStatusEnum] = None
    pod_parent_id: Optional[UUID] = None
    pod_parent_name: Optional[str] = None
    pod_parent_kind: Optional[PodParentTypeEnum] = None
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


class WorkloadRequestDecisionCreate(BaseModel):
    """
    Schema for creating a workload decision.
    """

    pod_id: UUID
    pod_name: str
    namespace: str
    node_id: UUID
    node_name: str
    is_elastic: bool
    queue_name: str
    demand_cpu: float
    demand_memory: float
    demand_slack_cpu: Optional[float] = None
    demand_slack_memory: Optional[float] = None
    decision_status: WorkloadRequestDecisionStatusEnum
    pod_parent_id: UUID
    pod_parent_name: str
    pod_parent_kind: PodParentTypeEnum
    created_at: Optional[datetime] = datetime.now(timezone.utc)
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
