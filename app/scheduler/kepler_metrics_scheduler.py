import asyncio
from app.services.kepler_metrics_service import KeplerMetricsService
from app.repositories.container_power_metrics import ContainerPowerMetricsRepository
from app.db.database import get_async_db
from sqlalchemy.ext.asyncio import AsyncSession
import logging

class KeplerMetricsScheduler:
    def __init__(self, interval_seconds: int = 60):
        self.interval_seconds = interval_seconds
        self.service = KeplerMetricsService()
        self._task = None
        self._running = False

    async def _run(self):
        self._running = True
        logging.info(f"KeplerMetricsScheduler started, interval: {self.interval_seconds} seconds")
        while self._running:
            try:
                logging.debug("KeplerMetricsScheduler: Starting scrape_and_store cycle...")
                # Get a new DB session for each run
                async for db in get_async_db():
                    await self.scrape_and_store(db)
                    break
            except Exception as e:
                logging.exception(f"Error in KeplerMetricsScheduler: {e}")
            await asyncio.sleep(self.interval_seconds)

    async def scrape_and_store(self, db: AsyncSession):
        metrics = await self.service.scrape_and_transform()
        logging.info(f"KeplerMetricsScheduler: Scraped {len(metrics)} metrics from Kepler endpoint.")
        repo = ContainerPowerMetricsRepository(db)
        for metric in metrics:
            logging.debug(f"Upserting metric: timestamp={metric.timestamp}, container_name={metric.container_name}, pod_name={metric.pod_name}, metric_source={metric.metric_source}")
            updated = await repo.update(metric.timestamp, metric.container_name, metric.pod_name, metric)
            if updated:
                logging.info(f"Updated metric for container={metric.container_name}, pod={metric.pod_name}, timestamp={metric.timestamp}")
            else:
                await repo.create(metric)
                logging.info(f"Created metric for container={metric.container_name}, pod={metric.pod_name}, timestamp={metric.timestamp}")
        logging.info(f"KeplerMetricsScheduler: Stored {len(metrics)} container power metrics from Kepler.")

    def start(self):
        if not self._task:
            logging.info("KeplerMetricsScheduler: Starting background task.")
            self._task = asyncio.create_task(self._run())

    def stop(self):
        logging.info("KeplerMetricsScheduler: Stopping background task.")
        self._running = False 