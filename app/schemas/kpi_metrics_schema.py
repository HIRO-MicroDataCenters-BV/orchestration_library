"""
Pydantic schemas for the KPI metrics.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class KPIMetricsBase(BaseModel):
    """
    Base schema for KPI metrics.
    """
    node_name: str
    cpu_utilization: Optional[float] = None
    mem_utilization: Optional[float] = None
    decision_time_in_seconds: Optional[float] = None


class KPIMetricsSchema(KPIMetricsBase):
    """
    Schema for KPI metrics with ID and creation timestamp.
    """
    id: int
    created_at: Optional[datetime] = None

    class Config:
        """
        Configuration class for Pydantic model.
        Provides settings for model behavior and validation.
        """
        orm_mode = True

        def get_orm_mode(self) -> bool:
            """
            Get the ORM mode setting.
            """
            return self.orm_mode

        def set_orm_mode(self, value: bool) -> None:
            """
            Set the ORM mode setting.
            """
            self.orm_mode = value


class KPIMetricsCreate(KPIMetricsBase):
    """
    Schema for creating new KPI metrics.
    """
