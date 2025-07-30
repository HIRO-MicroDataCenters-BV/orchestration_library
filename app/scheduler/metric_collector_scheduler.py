import asyncio
from app.services.unified_container_metrics_service import UnifiedContainerMetricsService
import logging

class MetricCollectorScheduler:
    def __init__(self, interval_seconds: int = 10):
        self.interval_seconds = interval_seconds
        self.service = UnifiedContainerMetricsService()
        self._task = None
        self._running = False

    async def _run(self):
        self._running = True
        logging.info(f"MetricCollectorScheduler started, interval: {self.interval_seconds} seconds")
        while self._running:
            try:
                logging.info("MetricCollectorScheduler: Starting unified metrics collection cycle...")
                stored_count = await self.service.collect_and_store_metrics()
                logging.info(f"MetricCollectorScheduler: Stored {stored_count} unified container metrics (Kepler + cAdvisor)")
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