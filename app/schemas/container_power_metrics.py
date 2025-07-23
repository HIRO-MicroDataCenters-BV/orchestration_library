"""
Container power metrics schemas.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class ContainerPowerMetricsBase(BaseModel):
    timestamp: datetime = Field(..., description="Timestamp (UTC, RFC3339)")
    container_name: Optional[str] = Field(None, description="Container name")
    pod_name: Optional[str] = Field(None, description="Pod name")
    namespace: Optional[str] = Field(None, description="Namespace")
    node_name: Optional[str] = Field(None, description="Node name")
    metric_source: Optional[str] = Field(None, description="Source of the metrics (e.g., 'kepler', 'cadvisor')")
    cpu_core_watts: Optional[float] = Field(None, description="CPU core power in watts")
    cpu_package_watts: Optional[float] = Field(None, description="CPU package power in watts")
    memory_power_watts: Optional[float] = Field(None, description="Memory power in watts")
    platform_watts: Optional[float] = Field(None, description="Platform power in watts")
    other_watts: Optional[float] = Field(None, description="Other power in watts")
    cpu_utilization_percent: Optional[float] = Field(None, description="CPU utilization percent")
    memory_utilization_percent: Optional[float] = Field(None, description="Memory utilization percent")
    memory_usage_bytes: Optional[int] = Field(None, description="Memory usage in bytes")
    network_io_rate_bytes_per_sec: Optional[float] = Field(None, description="Network IO rate in bytes/sec")
    disk_io_rate_bytes_per_sec: Optional[float] = Field(None, description="Disk IO rate in bytes/sec")

class ContainerPowerMetricsCreate(ContainerPowerMetricsBase):
    pass

class ContainerPowerMetricsUpdate(BaseModel):
    namespace: Optional[str] = None
    node_name: Optional[str] = None
    metric_source: Optional[str] = None
    cpu_core_watts: Optional[float] = None
    cpu_package_watts: Optional[float] = None
    memory_power_watts: Optional[float] = None
    platform_watts: Optional[float] = None
    other_watts: Optional[float] = None
    cpu_utilization_percent: Optional[float] = None
    memory_utilization_percent: Optional[float] = None
    memory_usage_bytes: Optional[int] = None
    network_io_rate_bytes_per_sec: Optional[float] = None
    disk_io_rate_bytes_per_sec: Optional[float] = None

class ContainerPowerMetricsResponse(ContainerPowerMetricsBase):
    class Config:
        from_attributes = True 