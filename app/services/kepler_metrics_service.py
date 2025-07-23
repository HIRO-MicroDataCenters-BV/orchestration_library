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
        from collections import defaultdict
        
        # Dictionary to group metrics by container
        container_metrics = defaultdict(dict)
        
        # Parse various Kepler metrics
        metric_patterns = {
            'core_joules': r'kepler_container_core_joules_total\{([^}]*)\} ([0-9.eE+-]+)',
            'dram_joules': r'kepler_container_dram_joules_total\{([^}]*)\} ([0-9.eE+-]+)',
            'package_joules': r'kepler_container_package_joules_total\{([^}]*)\} ([0-9.eE+-]+)',
            'uncore_joules': r'kepler_container_uncore_joules_total\{([^}]*)\} ([0-9.eE+-]+)'
        }
        
        # Extract metrics for each pattern
        for metric_type, pattern in metric_patterns.items():
            for match in re.finditer(pattern, metrics_text):
                labels_str, value = match.groups()
                labels = dict(re.findall(r'(\w+)="([^"]*)"', labels_str))
                
                # Create unique key for container
                container_key = (
                    labels.get("container_name", "unknown"),
                    labels.get("pod_name", "unknown"),
                    labels.get("container_namespace", "default")
                )
                
                # Store the metric value and labels
                if container_key not in container_metrics:
                    container_metrics[container_key] = {'labels': labels, 'metrics': {}}
                
                container_metrics[container_key]['metrics'][metric_type] = float(value)
        
        # Convert to ContainerPowerMetricsCreate objects
        results = []
        for container_key, data in container_metrics.items():
            labels = data['labels']
            metrics = data['metrics']
            
            # Calculate power from joules if watts not available
            cpu_power_watts = metrics.get('cpu_watts')
            if cpu_power_watts is None and 'cpu_joules' in metrics:
                # For joules, we would need previous measurements to calculate rate
                # For now, use core_joules as fallback for CPU power estimation
                if 'core_joules' in metrics:
                    # This is a rough estimation - in production you'd want proper rate calculation
                    cpu_power_watts = metrics['core_joules'] * 0.1  # Rough conversion factor
            
            # Memory power from DRAM joules
            memory_power_watts = None
            if 'dram_joules' in metrics:
                memory_power_watts = metrics['dram_joules'] * 0.05  # Rough conversion factor
            
            # Platform power from package joules
            platform_watts = None
            if 'package_joules' in metrics:
                platform_watts = metrics['package_joules'] * 0.08  # Rough conversion factor
            
            # Other power from uncore
            other_watts = None
            if 'uncore_joules' in metrics:
                other_watts = metrics['uncore_joules'] * 0.06  # Rough conversion factor
            
            results.append(ContainerPowerMetricsCreate(
                timestamp=datetime.now(timezone.utc),
                container_name=labels.get("container_name", "unknown"),
                pod_name=labels.get("pod_name", "unknown"),
                namespace=labels.get("container_namespace", None),
                node_name=labels.get("node_name", None),
                metric_source="kepler",
                cpu_power_watts=cpu_power_watts,
                memory_power_watts=memory_power_watts,
                platform_watts=platform_watts,
                other_watts=other_watts,
                cpu_utilization_percent=None,  # Not available in Kepler metrics
                memory_utilization_percent=None,  # Not available in Kepler metrics
                memory_usage_bytes=None,  # Not available in Kepler metrics
                network_io_rate_bytes_per_sec=None,  # Not available in Kepler metrics
                disk_io_rate_bytes_per_sec=None,  # Not available in Kepler metrics
            ))
        
        logging.info(f"KeplerMetricsService: Parsed {len(results)} container power metrics from Kepler.")
        return results

    async def scrape_and_transform(self) -> List[ContainerPowerMetricsCreate]:
        metrics_text = await self.fetch_metrics()
        logging.info("First 20 lines of Kepler metrics:\n" + '\n'.join(metrics_text.splitlines()[:20]))
        return self.parse_metrics(metrics_text) 