"""
SQLAlchemy models for the KPI metrics.
"""

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict

from app.schemas.tuning_parameter_schema import TuningParameterBase


class KPIMetricsGeometricMeanBase(BaseModel):
    """
    Base schema for KPI metrics geometric mean.
    """

    request_decision_id: UUID
    gm_cpu_utilization: float
    gm_mem_utilization: float
    gm_decision_time_in_seconds: float

class KPIMetricsGeometricMeanItem(KPIMetricsGeometricMeanBase):
    """
    Schema for a single KPI metrics geometric mean item.
    Matches columns from the kpi_metrics_geometric_mean view.
    """

    last_created_at: datetime
    last_seq_id: int

    model_config = ConfigDict(from_attributes=True)

class KPIMetricsGeometricMeanWithTuningParamsItem(KPIMetricsGeometricMeanBase, TuningParameterBase):
    """
    Schema for KPI metrics geometric mean item combined with tuning parameters.
    Inherits from both KPIMetricsGeometricMeanItem and TuningParameterResponse.
    """
    kpi_created_at: datetime
    tuning_param_created_at: datetime

    model_config = ConfigDict(from_attributes=True)
