"""
SQLAlchemy models for the KPI metrics.
"""

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class KPIMetricsGeometricMeanItem(BaseModel):
    """
    Schema for a single KPI metrics geometric mean item.
    Matches columns from the kpi_metrics_geometric_mean view.
    """

    request_decision_id: UUID
    gm_cpu_utilization: float
    gm_mem_utilization: float
    gm_decision_time_in_seconds: float
    last_created_at: datetime
    last_seq_id: int

    model_config = ConfigDict(from_attributes=True)
