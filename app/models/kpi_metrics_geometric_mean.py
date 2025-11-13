"""
SQLAlchemy models for the KPI metrics.
"""

from datetime import datetime
from sqlalchemy import (
    UUID,
    BigInteger,
    DateTime,
    Float,
)
from sqlalchemy.orm import mapped_column, Mapped
from app.db.database import Base
from app.models.base_dict_mixin import BaseDictMixin


class KPIMetricsGeometricMean(Base, BaseDictMixin):
    """
    ORM mapping to the VIEW: kpi_metrics_geomean.
    (created in Alembic migration
    alembic/versions/alembic/versions/
    018_3cd7bd1c74c5_Create_materialized_view_for_kpi_metrics_.py).
    Do not flush INSERT/UPDATE/DELETE against this model.

    Below tablename should be same as the view name in
    alembic/versions/alembic/versions/
    018_3cd7bd1c74c5_Create_materialized_view_for_kpi_metrics_.py
    """

    __tablename__ = "kpi_metrics_geometric_mean"
    __table_args__ = {"info": {"is_view": True}}

    request_decision_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), primary_key=True
    )
    gm_cpu_utilization: Mapped[float] = mapped_column(Float)
    gm_mem_utilization: Mapped[float] = mapped_column(Float)
    gm_decision_time_in_seconds: Mapped[float] = mapped_column(Float)
    last_created_at: Mapped[datetime] = mapped_column(DateTime)
    last_seq_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
