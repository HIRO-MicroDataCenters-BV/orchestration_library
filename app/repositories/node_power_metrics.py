"""
Repository for node power metrics data operations.
"""

from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.node_power_metrics import NodePowerMetrics
from app.schemas.node_power_metrics import NodePowerMetricsCreate

class NodePowerMetricsRepository:
    """Repository for node power metrics operations"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create_batch(self, metrics: List[NodePowerMetricsCreate]) -> List[NodePowerMetrics]:
        """Create multiple node power metrics records in batch"""
        db_metrics = []
        for metric in metrics:
            db_metric = NodePowerMetrics(**metric.model_dump())
            db_metrics.append(db_metric)
            self.session.add(db_metric)
        
        await self.session.commit()
        return db_metrics
    
    async def create(self, metric: NodePowerMetricsCreate) -> NodePowerMetrics:
        """Create a single node power metrics record"""
        db_metric = NodePowerMetrics(**metric.model_dump())
        self.session.add(db_metric)
        await self.session.commit()
        await self.session.refresh(db_metric)
        return db_metric