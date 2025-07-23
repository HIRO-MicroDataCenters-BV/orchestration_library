from sqlalchemy import Column, String, Float, BigInteger, DateTime


class ContainerPowerMetrics:
    """Database model for container power metrics based on db.sql schema"""
    __tablename__ = "container_power_metrics"

    # Primary key components
    timestamp = Column(DateTime, primary_key=True, nullable=False)
    container_name = Column(String(255), primary_key=True, nullable=False)
    pod_name = Column(String(255), primary_key=True, nullable=False)

    # Additional metadata
    namespace = Column(String(255))
    node_name = Column(String(255))
    metric_source = Column(String(255))

    # Power metrics (in watts - converted from joules)
    cpu_power_watts = Column(Float)
    memory_power_watts = Column(Float)
    platform_watts = Column(Float)
    other_watts = Column(Float)

    # Resource utilization metrics
    cpu_utilization_percent = Column(Float)
    memory_utilization_percent = Column(Float)
    memory_usage_bytes = Column(BigInteger)
    network_io_rate_bytes_per_sec = Column(Float)
    disk_io_rate_bytes_per_sec = Column(Float)

    def __repr__(self):
        return (f"<ContainerPowerMetrics("
                f"timestamp={self.timestamp}, "
                f"container={self.container_name}, "
                f"pod={self.pod_name}, "
                f"namespace={self.namespace}, "
                f"metric_source={self.metric_source})>")

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'container_name': self.container_name,
            'pod_name': self.pod_name,
            'namespace': self.namespace,
            'node_name': self.node_name,
            'metric_source': self.metric_source,
            'cpu_power_watts': self.cpu_power_watts,
            'memory_power_watts': self.memory_power_watts,
            'platform_watts': self.platform_watts,
            'other_watts': self.other_watts,
            'cpu_utilization_percent': self.cpu_utilization_percent,
            'memory_utilization_percent': self.memory_utilization_percent,
            'memory_usage_bytes': self.memory_usage_bytes,
            'network_io_rate_bytes_per_sec': self.network_io_rate_bytes_per_sec,
            'disk_io_rate_bytes_per_sec': self.disk_io_rate_bytes_per_sec,
        }
