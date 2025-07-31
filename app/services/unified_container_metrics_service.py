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
        Merge cAdvisor and Kepler metrics based on container_id.
        Logic: For each Kepler metric, find matching cAdvisor metric by container_id,
        then add CPU and memory data from cAdvisor to the Kepler metric.
        """
        merged_metrics = []
        
        # Create lookup dict for cAdvisor metrics by container_id
        cadvisor_lookup = {}
        for metric in cadvisor_metrics:
            if metric.container_id:
                cadvisor_lookup[metric.container_id] = metric
        
        # Process each Kepler metric
        for kepler_metric in kepler_metrics:
            if not kepler_metric.container_id:
                # Skip Kepler metrics without container_id
                continue
                
            # Find matching cAdvisor metric by container_id
            cadvisor_metric = cadvisor_lookup.get(kepler_metric.container_id)
            
            # Create unified metric by enhancing Kepler metric with cAdvisor CPU/memory data
            unified_metric = self._create_unified_metric_from_kepler(kepler_metric, cadvisor_metric)
            if unified_metric:
                merged_metrics.append(unified_metric)
        
        logging.info(f"Merged {len(kepler_metrics)} Kepler metrics with cAdvisor CPU/memory data = {len(merged_metrics)} unified metrics")
        return merged_metrics

    def _create_unified_metric_from_kepler(
        self, 
        kepler_metric: ContainerPowerMetricsCreate,
        cadvisor_metric: Optional[ContainerPowerMetricsCreate]
    ) -> Optional[ContainerPowerMetricsCreate]:
        """
        Create a unified metric by enhancing Kepler metric with cAdvisor CPU/memory data.
        Keep all Kepler data unchanged, only add CPU and memory metrics from cAdvisor.
        """
        # Use current timestamp
        timestamp = datetime.utcnow()
        
        # Determine metric source
        metric_source = "kepler"
        if cadvisor_metric:
            metric_source = "kepler+cadvisor"
        
        # Helper function to round float values to 4 decimal places
        def round_float(value):
            return round(value, 4) if value is not None else None
        
        # Create unified metric keeping all Kepler data and adding cAdvisor CPU/memory
        return ContainerPowerMetricsCreate(
            timestamp=timestamp,
            container_name=kepler_metric.container_name,
            container_id=kepler_metric.container_id,  # Keep container_id for internal use
            pod_name=kepler_metric.pod_name,
            namespace=kepler_metric.namespace,
            node_name=kepler_metric.node_name,
            metric_source=metric_source,
            
            # Keep all Kepler energy data unchanged but rounded to 4 decimal places
            cpu_core_watts=round_float(kepler_metric.cpu_core_watts),
            cpu_package_watts=round_float(kepler_metric.cpu_package_watts),
            memory_power_watts=round_float(kepler_metric.memory_power_watts),
            platform_watts=round_float(kepler_metric.platform_watts),
            other_watts=round_float(kepler_metric.other_watts),
            
            # Add CPU and memory utilization data from cAdvisor (if available) - rounded to 4 decimal places
            cpu_utilization_percent=round_float(cadvisor_metric.cpu_utilization_percent) if cadvisor_metric else None,
            memory_utilization_percent=round_float(cadvisor_metric.memory_utilization_percent) if cadvisor_metric else None,
            memory_usage_bytes=cadvisor_metric.memory_usage_bytes if cadvisor_metric else None,  # Keep bytes as integer
            
            # Network and disk IO (not used currently)
            network_io_rate_bytes_per_sec=None,
            disk_io_rate_bytes_per_sec=None,
        )

    def _create_unified_metric(
        self, 
        cadvisor_metric: Optional[ContainerPowerMetricsCreate],
        kepler_metric: Optional[ContainerPowerMetricsCreate],
        container_key: tuple
    ) -> Optional[ContainerPowerMetricsCreate]:
        """
        Legacy method - kept for compatibility but not used in new merge logic.
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
        
        # Helper function to round float values to 4 decimal places
        def round_float(value):
            return round(value, 4) if value is not None else None
        
        # Create unified metric with data from both sources
        return ContainerPowerMetricsCreate(
            timestamp=timestamp,
            container_name=container_name,
            container_id=kepler_metric.container_id if kepler_metric else cadvisor_metric.container_id if cadvisor_metric else None,
            pod_name=pod_name,
            namespace=namespace,
            node_name=node_name,
            metric_source=metric_source,
            
            # Energy data from Kepler (if available) - rounded to 4 decimal places
            cpu_core_watts=round_float(kepler_metric.cpu_core_watts) if kepler_metric else None,
            cpu_package_watts=round_float(kepler_metric.cpu_package_watts) if kepler_metric else None,
            memory_power_watts=round_float(kepler_metric.memory_power_watts) if kepler_metric else None,
            platform_watts=round_float(kepler_metric.platform_watts) if kepler_metric else None,
            other_watts=round_float(kepler_metric.other_watts) if kepler_metric else None,
            
            # Usage data from cAdvisor (if available) - rounded to 4 decimal places
            cpu_utilization_percent=round_float(cadvisor_metric.cpu_utilization_percent) if cadvisor_metric else None,
            memory_utilization_percent=round_float(cadvisor_metric.memory_utilization_percent) if cadvisor_metric else None,
            memory_usage_bytes=cadvisor_metric.memory_usage_bytes if cadvisor_metric else None,  # Keep bytes as integer
            
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