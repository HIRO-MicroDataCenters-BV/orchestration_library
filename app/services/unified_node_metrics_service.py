"""
Unified node metrics service that combines cAdvisor and Kepler node-level metrics.
"""

import asyncio
from datetime import datetime
from typing import List, Dict, Optional
from app.services.cadvisor_metrics_service import CadvisorMetricsService
from app.services.kepler_node_metrics_service import KeplerNodeMetricsService
from app.schemas.node_power_metrics import NodePowerMetricsCreate
from app.repositories.node_power_metrics import NodePowerMetricsRepository
from app.db.database import get_async_db
import logging

class UnifiedNodeMetricsService:
    """
    Service that combines metrics from both cAdvisor (CPU/memory usage) 
    and Kepler (energy consumption) into unified node power metrics.
    """
    
    def __init__(self):
        self.cadvisor_service = CadvisorMetricsService()
        self.kepler_node_service = KeplerNodeMetricsService()
        
    async def collect_and_store_metrics(self) -> int:
        """
        Collect node metrics from both cAdvisor and Kepler, merge them, and store in database.
        Returns the number of records stored.
        """
        try:
            # Collect node metrics from Kepler
            kepler_node_metrics = await self.kepler_node_service.scrape_and_transform()
            
            # TODO: Add cAdvisor node-level metrics collection if needed
            # For now, we'll just use Kepler metrics
            
            # Store in database
            stored_count = await self._store_metrics(kepler_node_metrics)
            
            logging.info(f"UnifiedNodeMetricsService: Stored {stored_count} node power metrics")
            return stored_count
            
        except Exception as e:
            logging.error(f"Error in collect_and_store_node_metrics: {e}")
            return 0

    async def _store_metrics(self, metrics: List[NodePowerMetricsCreate]) -> int:
        """Store node metrics in the database."""
        if not metrics:
            return 0
            
        stored_count = 0
        async for session in get_async_db():
            try:
                repository = NodePowerMetricsRepository(session)
                
                for metric in metrics:
                    try:
                        await repository.create(metric)
                        stored_count += 1
                    except Exception as e:
                        logging.warning(f"Failed to store node metric for {metric.node_name}: {e}")
                        
                await session.commit()
                
            except Exception as e:
                logging.error(f"Database error storing node metrics: {e}")
                await session.rollback()
                
        return stored_count

    async def get_latest_metrics(
        self,
        node_name: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """Get latest node metrics from database."""
        async for session in get_async_db():
            try:
                # TODO: Implement repository method to get node metrics
                # repository = NodePowerMetricsRepository(session)
                # metrics = await repository.get_all(node_name=node_name, limit=limit)
                # return [metric.to_dict() for metric in metrics]
                return []
            except Exception as e:
                logging.error(f"Error retrieving node metrics: {e}")
                return []
        return []  # Fallback if no session is available