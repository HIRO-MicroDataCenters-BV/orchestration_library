import aiohttp
from datetime import datetime, timezone
from typing import List
from app.schemas.container_power_metrics import ContainerPowerMetricsCreate
import logging

class KeplerMetricsService:
    KEPLER_METRICS_URL = "http://localhost:9102/metrics"

    async def fetch_metrics(self) -> str:
        async with aiohttp.ClientSession() as session:
            async with session.get(self.KEPLER_METRICS_URL) as resp:
                resp.raise_for_status()
                return await resp.text()

    def parse_metrics(self, metrics_text: str) -> List[ContainerPowerMetricsCreate]:
        """
        Parse Prometheus metrics text and extract container energy metrics.
        Returns a list of ContainerPowerMetricsCreate objects.
        """
        import re
        results = []
        # Regex for kepler_container_core_joules_total
        pattern = re.compile(r'kepler_container_core_joules_total\{([^}]*)\} ([0-9.eE+-]+)')
        for match in pattern.finditer(metrics_text):
            labels_str, value = match.groups()
            labels = dict(re.findall(r'(\w+)="([^"]*)"', labels_str))
            core_joules_total = float(value)
            results.append(ContainerPowerMetricsCreate(
                timestamp=datetime.now(timezone.utc),
                container_name=labels.get("container_name", "unknown"),
                pod_name=labels.get("pod_name", "unknown"),
                namespace=labels.get("container_namespace", None),
                node_name=None,  # Not present in this metric
                # Store joules in a custom field; you may want to add this to your schema/model
                cpu_power_watts=None,
                memory_power_watts=None,
                other_watts=None,
                total_watts=None,
                cpu_utilization_percent=None,
                memory_utilization_percent=None,
                memory_usage_bytes=None,
                network_io_rate_bytes_per_sec=None,
                disk_io_rate_bytes_per_sec=None,
                # Custom field for joules
                core_joules_total=core_joules_total
            ))
        logging.info(f"KeplerMetricsService: Parsed {len(results)} kepler_container_core_joules_total metrics.")
        return results

    async def scrape_and_transform(self) -> List[ContainerPowerMetricsCreate]:
        metrics_text = await self.fetch_metrics()
        logging.info("First 20 lines of Kepler metrics:\n" + '\n'.join(metrics_text.splitlines()[:20]))
        return self.parse_metrics(metrics_text) 