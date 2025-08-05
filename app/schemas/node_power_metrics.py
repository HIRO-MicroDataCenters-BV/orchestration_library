"""
Node power metrics schemas for API and service layer.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class NodePowerMetricsCreate(BaseModel):
    """Schema for creating node power metrics"""
    timestamp: datetime
    node_name: str
    metric_source: str
    cpu_core_watts: Optional[float] = None
    cpu_package_watts: Optional[float] = None
    memory_power_watts: Optional[float] = None
    platform_watts: Optional[float] = None
    cpu_utilization_percent: Optional[float] = None
    memory_utilization_percent: Optional[float] = None

class NodePowerMetricsResponse(BaseModel):
    """Schema for node power metrics API response"""
    timestamp: datetime
    node_name: str
    metric_source: str
    cpu_core_watts: Optional[float] = None
    cpu_package_watts: Optional[float] = None
    memory_power_watts: Optional[float] = None
    platform_watts: Optional[float] = None
    cpu_utilization_percent: Optional[float] = None
    memory_utilization_percent: Optional[float] = None

    class Config:
        from_attributes = True