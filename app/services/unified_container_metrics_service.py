"""
Unified container metrics service that combines cAdvisor and Kepler metrics.
"""

import asyncio
from datetime import datetime
from typing import List, Dict, Optional
from app.services.cadvisor_metrics_service import CadvisorMetricsService
from app.services.kepler_metrics_service import KeplerMetricsService
from app.schemas.container_power_metrics import ContainerPowerMetricsCreate
from app.repositories.container_power_metrics import ContainerPowerMetricsRepository
from app.db.database import get_async_db
import logging

class UnifiedContainerMetricsService:
    """
    Service that combines metrics from both cAdvisor (CPU/memory usage) 
    and Kepler (energy consumption) into unified container power metrics.
    """
    
    def __init__(self):
        self.cadvisor_service = CadvisorMetricsService()
        self.kepler_service = KeplerMetricsService()
        
    async def collect_and_store_metrics(self) -> int:
        """
        Collect metrics from both cAdvisor and Kepler, merge them, and store in database.
        Returns the number of records stored.
        """
        try:
            # Collect metrics from both sources concurrently
            cadvisor_task = asyncio.create_task(self.cadvisor_service.scrape_and_transform())
            kepler_task = asyncio.create_task(self.kepler_service.scrape_and_transform())
            
            cadvisor_metrics, kepler_metrics = await asyncio.gather(
                cadvisor_task, kepler_task, return_exceptions=True
            )
            
            # Handle potential exceptions
            if isinstance(cadvisor_metrics, Exception):
                logging.error(f"Failed to collect cAdvisor metrics: {cadvisor_metrics}")
                cadvisor_metrics = []
            if isinstance(kepler_metrics, Exception):
                logging.error(f"Failed to collect Kepler metrics: {kepler_metrics}")
                kepler_metrics = []
                
            # Merge metrics from both sources
            unified_metrics = self._merge_metrics(cadvisor_metrics, kepler_metrics)
            
            # Store in database
            stored_count = await self._store_metrics(unified_metrics)
            
            logging.info(f"UnifiedContainerMetricsService: Stored {stored_count} unified container metrics")
            return stored_count
            
        except Exception as e:
            logging.error(f"Error in collect_and_store_metrics: {e}")
            return 0

    def _merge_metrics(
        self, 
        cadvisor_metrics: List[ContainerPowerMetricsCreate], 
        kepler_metrics: List[ContainerPowerMetricsCreate]
    ) -> List[ContainerPowerMetricsCreate]:
        """
        Merge cAdvisor and Kepler metrics based on container_name, pod_name, and namespace.
        Priority: Start with Kepler metrics (energy data) and supplement with cAdvisor data (CPU/memory usage).
        """
        merged_metrics = []
        
        # Create lookup dict for cAdvisor metrics
        cadvisor_lookup = {}
        for metric in cadvisor_metrics:
            key = (metric.container_name, metric.pod_name, metric.namespace)
            cadvisor_lookup[key] = metric
        
        # Create lookup dict for Kepler metrics
        kepler_lookup = {}
        for metric in kepler_metrics:
            key = (metric.container_name, metric.pod_name, metric.namespace)
            kepler_lookup[key] = metric
        
        # Get all unique container keys from both sources
        all_keys = set(cadvisor_lookup.keys()) | set(kepler_lookup.keys())
        
        for key in all_keys:
            cadvisor_metric = cadvisor_lookup.get(key)
            kepler_metric = kepler_lookup.get(key)
            
            # Create unified metric object
            unified_metric = self._create_unified_metric(cadvisor_metric, kepler_metric, key)
            if unified_metric:
                merged_metrics.append(unified_metric)
        
        logging.info(f"Merged {len(cadvisor_metrics)} cAdvisor + {len(kepler_metrics)} Kepler = {len(merged_metrics)} unified metrics")
        return merged_metrics

    def _create_unified_metric(
        self, 
        cadvisor_metric: Optional[ContainerPowerMetricsCreate],
        kepler_metric: Optional[ContainerPowerMetricsCreate],
        container_key: tuple
    ) -> Optional[ContainerPowerMetricsCreate]:
        """
        Create a unified metric object combining data from both sources.
        """
        container_name, pod_name, namespace = container_key
        
        # Use current timestamp
        timestamp = datetime.utcnow()
        
        # Determine the primary source and node name
        node_name = None
        if kepler_metric:
            node_name = kepler_metric.node_name
        elif cadvisor_metric:
            node_name = cadvisor_metric.node_name
            
        # Combine metric sources
        metric_sources = []
        if cadvisor_metric:
            metric_sources.append("cadvisor")
        if kepler_metric:
            metric_sources.append("kepler")
        metric_source = "+".join(metric_sources)
        
        # Create unified metric with data from both sources
        return ContainerPowerMetricsCreate(
            timestamp=timestamp,
            container_name=container_name,
            pod_name=pod_name,
            namespace=namespace,
            node_name=node_name,
            metric_source=metric_source,
            
            # Energy data from Kepler (if available)
            cpu_core_watts=kepler_metric.cpu_core_watts if kepler_metric else None,
            cpu_package_watts=kepler_metric.cpu_package_watts if kepler_metric else None,
            memory_power_watts=kepler_metric.memory_power_watts if kepler_metric else None,
            platform_watts=kepler_metric.platform_watts if kepler_metric else None,
            other_watts=kepler_metric.other_watts if kepler_metric else None,
            
            # Usage data from cAdvisor (if available)
            cpu_utilization_percent=cadvisor_metric.cpu_utilization_percent if cadvisor_metric else None,
            memory_utilization_percent=cadvisor_metric.memory_utilization_percent if cadvisor_metric else None,
            memory_usage_bytes=cadvisor_metric.memory_usage_bytes if cadvisor_metric else None,
            
            # Network and disk IO (could be extended)
            network_io_rate_bytes_per_sec=None,
            disk_io_rate_bytes_per_sec=None,
        )

    async def _store_metrics(self, metrics: List[ContainerPowerMetricsCreate]) -> int:
        """Store unified metrics in the database."""
        if not metrics:
            return 0
            
        stored_count = 0
        async for session in get_async_db():
            try:
                repository = ContainerPowerMetricsRepository(session)
                
                for metric in metrics:
                    try:
                        await repository.create(metric)
                        stored_count += 1
                    except Exception as e:
                        logging.warning(f"Failed to store metric for {metric.container_name}: {e}")
                        
                await session.commit()
                
            except Exception as e:
                logging.error(f"Database error storing metrics: {e}")
                await session.rollback()
                
        return stored_count

    async def get_latest_metrics(
        self,
        container_name: Optional[str] = None,
        pod_name: Optional[str] = None,
        namespace: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """Get latest unified metrics from database."""
        async for session in get_async_db():
            try:
                repository = ContainerPowerMetricsRepository(session)
                metrics = await repository.get_all(
                    container_name=container_name,
                    pod_name=pod_name,
                    namespace=namespace,
                    limit=limit
                )
                return [metric.to_dict() for metric in metrics]
            except Exception as e:
                logging.error(f"Error retrieving metrics: {e}")
                return []
        return []  # Fallback if no session is available