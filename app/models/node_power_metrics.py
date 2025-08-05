"""
Node power metrics model.
"""

from sqlalchemy import Column, String, DateTime, Float, PrimaryKeyConstraint
from app.db.database import Base

class NodePowerMetrics(Base):
    """Database model for node power metrics from Kepler"""
    __tablename__ = "node_power_metrics"

    # Primary key components
    timestamp = Column(DateTime, nullable=False)
    node_name = Column(String(255))

    # Additional metadata
    metric_source = Column(String(255))

    # Power metrics (from Kepler) - sum of all this is the total power consumption in watts
    cpu_core_watts = Column(Float)
    cpu_package_watts = Column(Float)
    memory_power_watts = Column(Float)
    platform_watts = Column(Float)

    # Resource utilization (from cAdvisor)
    cpu_utilization_percent = Column(Float)
    memory_utilization_percent = Column(Float)

    __table_args__ = (
        PrimaryKeyConstraint('timestamp', 'node_name'),
    )

    def __repr__(self):
        return (f"<NodePowerMetrics("
                f"timestamp={self.timestamp}, "
                f"node={self.node_name}, "
                f"metric_source={self.metric_source})>")

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'node_name': self.node_name,
            'metric_source': self.metric_source,
            'cpu_core_watts': self.cpu_core_watts,
            'cpu_package_watts': self.cpu_package_watts,
            'memory_power_watts': self.memory_power_watts,
            'platform_watts': self.platform_watts,
            'cpu_utilization_percent': self.cpu_utilization_percent,
            'memory_utilization_percent': self.memory_utilization_percent,
        }