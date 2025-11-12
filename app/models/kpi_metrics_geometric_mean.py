"""
SQLAlchemy models for the KPI metrics.
"""

from sqlalchemy import (
    UUID,
    Column,
    DateTime,
    Double,
    Integer,
)
from app.db.database import Base
from app.models.base_dict_mixin import BaseDictMixin


class KPIMetricsGeometricMean(Base, BaseDictMixin):
    """
    ORM mapping to the VIEW: kpi_metrics_geomean.
    (created in Alembic migration 
    alembic/versions/alembic/versions/018_3cd7bd1c74c5_Create_materialized_view_for_kpi_metrics_.py).
    Do not flush INSERT/UPDATE/DELETE against this model.

    Below tablename should be same as the view name in 
    alembic/versions/alembic/versions/018_3cd7bd1c74c5_Create_materialized_view_for_kpi_metrics_.py
    """

    __tablename__ = "kpi_metrics_geometric_mean"
    __table_args__ = {"info": {"is_view": True}}

    request_decision_id = Column(UUID(as_uuid=True), unique=False, nullable=False)
    gm_cpu_utilization = Column(Double)
    gm_mem_utilization = Column(Double)
    gm_decision_time_in_seconds = Column(Double)
    last_created_at = Column(DateTime)
    last_seq_id = Column(Integer)