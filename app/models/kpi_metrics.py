"""
SQLAlchemy models for the KPI metrics.
"""

from sqlalchemy import (
    UUID,
    Column,
    Double,
    Integer,
    String,
    TIMESTAMP,
    text,
)
from app.db.database import Base
from app.models.base_dict_mixin import BaseDictMixin


class KPIMetrics(Base, BaseDictMixin):
    """
    Model representing the KPI metrics.
    """

    __tablename__ = "kpi_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    request_decision_id = Column(UUID(as_uuid=True), unique=False, nullable=False)
    node_name = Column(String(1024), nullable=False)
    cpu_utilization = Column(Double)
    mem_utilization = Column(Double)
    decision_time_in_seconds = Column(Double)
    created_at = Column(
        TIMESTAMP(timezone=True), server_default=text("now()"), index=True
    )
