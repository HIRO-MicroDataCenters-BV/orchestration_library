import aiohttp
import re
from collections import defaultdict
from datetime import datetime, timezone
from typing import List
from app.schemas.node_power_metrics import NodePowerMetricsCreate
import logging

class KeplerNodeMetricsService:
    KEPLER_METRICS_URL = "http://localhost:9102/metrics"
    
    def __init__(self):
        # Store previous measurements for rate calculation
        self._previous_metrics = {}

    async def fetch_metrics(self) -> str:
        async with aiohttp.ClientSession() as session:
            async with session.get(self.KEPLER_METRICS_URL) as resp:
                resp.raise_for_status()
                return await resp.text()

    def parse_metrics(self, metrics_text: str) -> List[NodePowerMetricsCreate]:
        """
        Parse Prometheus metrics text and extract node energy metrics.
        Returns a list of NodePowerMetricsCreate objects.
        """
        
        # Dictionary to group metrics by node
        node_metrics = defaultdict(dict)
        
        # Parse various Kepler node metrics
        metric_patterns = {
            'core_joules': r'kepler_node_core_joules_total\{([^}]*)\} ([0-9.eE+-]+)',
            'package_joules': r'kepler_node_package_joules_total\{([^}]*)\} ([0-9.eE+-]+)',
            'dram_joules': r'kepler_node_dram_joules_total\{([^}]*)\} ([0-9.eE+-]+)',
            'platform_joules': r'kepler_node_platform_joules_total\{([^}]*)\} ([0-9.eE+-]+)',
        }
        
        # Extract metrics for each pattern
        for metric_type, pattern in metric_patterns.items():
            for match in re.finditer(pattern, metrics_text):
                labels_str, value = match.groups()
                labels = dict(re.findall(r'(\w+)="([^"]*)"', labels_str))
                
                # Get node identifier
                node_name = labels.get("instance", "unknown")
                
                # Store the metric value and labels
                if node_name not in node_metrics:
                    node_metrics[node_name] = {'labels': labels, 'metrics': {}}
                
                node_metrics[node_name]['metrics'][metric_type] = float(value)
        
        # Convert to NodePowerMetricsCreate objects
        results = []
        current_time = datetime.utcnow()
        
        for node_name, data in node_metrics.items():
            labels = data['labels']
            metrics = data['metrics']
            
            # Get previous metrics for this node if they exist
            previous_data = self._previous_metrics.get(node_name)
            
            # Calculate watts from joules using rate of change
            cpu_core_watts = self._calculate_watts('core_joules', metrics, previous_data)
            cpu_package_watts = self._calculate_watts('package_joules', metrics, previous_data)
            memory_power_watts = self._calculate_watts('dram_joules', metrics, previous_data)
            platform_watts = self._calculate_watts('platform_joules', metrics, previous_data)
            
            # Store current metrics for next calculation
            self._previous_metrics[node_name] = {
                'timestamp': current_time,
                'metrics': metrics.copy()
            }
            
            results.append(NodePowerMetricsCreate(
                timestamp=datetime.utcnow(),
                node_name=node_name,
                metric_source="kepler",
                cpu_core_watts=cpu_core_watts,
                cpu_package_watts=cpu_package_watts,
                memory_power_watts=memory_power_watts,
                platform_watts=platform_watts,
                cpu_utilization_percent=None,  # Not available in Kepler metrics
                memory_utilization_percent=None,  # Not available in Kepler metrics
            ))
        
        logging.info(f"KeplerNodeMetricsService: Parsed {len(results)} node power metrics from Kepler.")
        return results

    def _calculate_watts(self, metric_key: str, current_metrics: dict, previous_data: dict) -> float:
        """
        Calculate watts from joules using rate of change.
        Watts = (current_joules - previous_joules) / time_diff_seconds
        """
        if metric_key not in current_metrics:
            return 0.0
            
        current_joules = current_metrics[metric_key]
        
        # If no previous data, use a fallback estimation
        if not previous_data or metric_key not in previous_data['metrics']:
            # Fallback: assume a small time window and estimate based on cumulative value
            # This is still an approximation but better than arbitrary factors
            estimated_watts = current_joules / 3600  # Assume values accumulated over 1 hour
            return max(0.0, estimated_watts)  # Ensure non-negative
        
        previous_joules = previous_data['metrics'][metric_key]
        time_diff = (datetime.utcnow() - previous_data['timestamp']).total_seconds()
        
        # Calculate rate: joules per second = watts
        if time_diff > 0:
            joules_diff = current_joules - previous_joules
            watts = joules_diff / time_diff
            return max(0.0, watts)  # Ensure non-negative (handle counter resets)
        
        return 0.0

    async def scrape_and_transform(self) -> List[NodePowerMetricsCreate]:
        metrics_text = await self.fetch_metrics()
        logging.info("First 11 lines of Kepler node metrics:\n" + '\n'.join(metrics_text.splitlines()[:2]))
        return self.parse_metrics(metrics_text)