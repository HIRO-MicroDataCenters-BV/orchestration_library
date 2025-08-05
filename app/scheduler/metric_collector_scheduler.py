import asyncio
from app.services.unified_container_metrics_service import UnifiedContainerMetricsService
from app.services.unified_node_metrics_service import UnifiedNodeMetricsService
import logging

class MetricCollectorScheduler:
    def __init__(self, interval_seconds: int = 10):
        self.interval_seconds = interval_seconds
        self.container_service = UnifiedContainerMetricsService()
        self.node_service = UnifiedNodeMetricsService()
        self._task = None
        self._running = False

    async def _run(self):
        self._running = True
        logging.info(f"MetricCollectorScheduler started, interval: {self.interval_seconds} seconds")
        while self._running:
            try:
                logging.info("MetricCollectorScheduler: Starting unified metrics collection cycle...")
                
                # Collect container and node metrics concurrently
                container_task = asyncio.create_task(self.container_service.collect_and_store_metrics())
                node_task = asyncio.create_task(self.node_service.collect_and_store_metrics())
                
                container_count, node_count = await asyncio.gather(
                    container_task, node_task, return_exceptions=True
                )
                
                # Handle potential exceptions
                if isinstance(container_count, Exception):
                    logging.error(f"Failed to collect container metrics: {container_count}")
                    container_count = 0
                if isinstance(node_count, Exception):
                    logging.error(f"Failed to collect node metrics: {node_count}")
                    node_count = 0
                
                logging.info(f"MetricCollectorScheduler: Stored {container_count} container metrics and {node_count} node metrics")
            except Exception as e:
                logging.exception(f"Error in MetricCollectorScheduler: {e}")
            await asyncio.sleep(self.interval_seconds)

    def start(self):
        if not self._task:
            logging.info("MetricCollectorScheduler: Starting background task.")
            self._task = asyncio.create_task(self._run())

    def stop(self):
        logging.info("MetricCollectorScheduler: Stopping background task.")
        self._running = False 