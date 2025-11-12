"""
SQLAlchemy models for the KPI metrics.
"""

from datetime import datetime
from uuid import UUID
from typing import Optional
from pydantic import BaseModel


class KPIMetricsGeometricMeanItem(BaseModel):
    """
    Schema for a single KPI metrics geometric mean item.
    Matches columns from the kpi_metrics_geometric_mean view.
    """
    request_decision_id: UUID
    gm_cpu_utilization: Optional[float] = None
    gm_mem_utilization: Optional[float] = None
    gm_decision_time_in_seconds: Optional[float] = None
    last_created_at: Optional[datetime] = None
    last_seq_id: Optional[int] = None
