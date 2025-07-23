"""
Container power metrics model.
"""

from sqlalchemy import Column, String, DateTime, Float, BigInteger, PrimaryKeyConstraint
from app.db.database import Base

class ContainerPowerMetrics(Base):
    __tablename__ = "container_power_metrics"
    timestamp = Column(DateTime(timezone=True), nullable=False)
    container_name = Column(String(255), nullable=False)
    pod_name = Column(String(255), nullable=False)
    namespace = Column(String(255))
    node_name = Column(String(255))

    cpu_power_watts = Column(Float)
    memory_power_watts = Column(Float)
    other_watts = Column(Float)
    total_watts = Column(Float)

    cpu_utilization_percent = Column(Float)
    memory_utilization_percent = Column(Float)
    memory_usage_bytes = Column(BigInteger)
    network_io_rate_bytes_per_sec = Column(Float)
    disk_io_rate_bytes_per_sec = Column(Float)

    __table_args__ = (
        PrimaryKeyConstraint('timestamp', 'container_name', 'pod_name'),
    ) 