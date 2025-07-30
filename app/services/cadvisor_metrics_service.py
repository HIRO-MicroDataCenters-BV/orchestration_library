
import aiohttp
import re
from datetime import datetime
from typing import List, Dict, Any
from collections import defaultdict
from app.schemas.container_power_metrics import ContainerPowerMetricsCreate
import logging

class CadvisorMetricsService:
    CADVISOR_METRICS_URL = "http://localhost:8080/metrics"
    
    def __init__(self):
        self._previous_metrics = {}

    async def fetch_metrics(self) -> str:
        """Fetch metrics from cAdvisor Prometheus endpoint."""
        async with aiohttp.ClientSession() as session:
            async with session.get(self.CADVISOR_METRICS_URL) as resp:
                resp.raise_for_status()
                return await resp.text()

    def parse_metrics(self, metrics_text: str) -> List[ContainerPowerMetricsCreate]:
        """
        Parse cAdvisor Prometheus metrics and extract CPU and memory usage.
        Returns a list of ContainerPowerMetricsCreate objects.
        """
        container_metrics = defaultdict(dict)
        
        # Metrics patterns for cAdvisor
        metric_patterns = {
            'cpu_usage_seconds_total': r'container_cpu_usage_seconds_total\{([^}]*)\} ([0-9.eE+-]+)',
            'memory_usage_bytes': r'container_memory_usage_bytes\{([^}]*)\} ([0-9.eE+-]+)',
            'cpu_system_seconds_total': r'container_cpu_system_seconds_total\{([^}]*)\} ([0-9.eE+-]+)',
            'cpu_user_seconds_total': r'container_cpu_user_seconds_total\{([^}]*)\} ([0-9.eE+-]+)',
        }
        
        # Extract metrics for each pattern
        for metric_type, pattern in metric_patterns.items():
            for match in re.finditer(pattern, metrics_text):
                labels_str, value = match.groups()
                labels = dict(re.findall(r'(\w+)="([^"]*)"', labels_str))
                
                # Skip metrics without container names or system containers
                container_name = labels.get("name", "")
                if not container_name or container_name.startswith("/system"):
                    continue
                    
                # Create unique key for container
                pod_name = labels.get("pod_name", labels.get("pod", "unknown"))
                namespace = labels.get("namespace", "default")
                
                container_key = (container_name, pod_name, namespace)
                
                # Store the metric value and labels
                if container_key not in container_metrics:
                    container_metrics[container_key] = {'labels': labels, 'metrics': {}}
                
                container_metrics[container_key]['metrics'][metric_type] = float(value)
        
        # Convert to ContainerPowerMetricsCreate objects
        results = []
        current_time = datetime.utcnow()
        
        for container_key, data in container_metrics.items():
            labels = data['labels']
            metrics = data['metrics']
            container_id = f"{container_key[0]}_{container_key[1]}_{container_key[2]}"
            
            # Get previous metrics for this container if they exist
            previous_data = self._previous_metrics.get(container_id)
            
            # Calculate CPU utilization percentage
            cpu_utilization_percent = self._calculate_cpu_utilization(metrics, previous_data)
            
            # Get memory usage in bytes
            memory_usage_bytes = int(metrics.get('memory_usage_bytes', 0))
            
            # Calculate memory utilization percentage (would need memory limits from cAdvisor)
            memory_utilization_percent = self._calculate_memory_utilization(metrics, labels)
            
            # Store current metrics for next calculation
            self._previous_metrics[container_id] = {
                'timestamp': current_time,
                'metrics': metrics.copy()
            }
            
            # Clean container name (remove leading slash if present)
            clean_container_name = labels.get("name", "").lstrip("/")
            
            results.append(ContainerPowerMetricsCreate(
                timestamp=current_time,
                container_name=clean_container_name,
                pod_name=pod_name,
                namespace=namespace,
                node_name=labels.get("node", labels.get("node_name", None)),
                metric_source="cadvisor",
                cpu_core_watts=None,  # Not available in cAdvisor
                cpu_package_watts=None,  # Not available in cAdvisor  
                memory_power_watts=None,  # Not available in cAdvisor
                platform_watts=None,  # Not available in cAdvisor
                other_watts=None,  # Not available in cAdvisor
                cpu_utilization_percent=cpu_utilization_percent,
                memory_utilization_percent=memory_utilization_percent,
                memory_usage_bytes=memory_usage_bytes,
                network_io_rate_bytes_per_sec=None,  # Could be added if needed
                disk_io_rate_bytes_per_sec=None,  # Could be added if needed
            ))
        
        logging.info(f"CadvisorMetricsService: Parsed {len(results)} container metrics from cAdvisor.")
        return results

    def _calculate_cpu_utilization(self, current_metrics: Dict[str, float], previous_data: Dict[str, Any]) -> float:
        """
        Calculate CPU utilization percentage from cpu_usage_seconds_total.
        CPU utilization = (delta_cpu_seconds / delta_time_seconds) * 100
        """
        cpu_usage_total = current_metrics.get('cpu_usage_seconds_total', 0)
        
        if not previous_data or 'cpu_usage_seconds_total' not in previous_data['metrics']:
            return 0.0
            
        previous_cpu_usage = previous_data['metrics']['cpu_usage_seconds_total']
        time_diff = (datetime.utcnow() - previous_data['timestamp']).total_seconds()
        
        if time_diff > 0:
            cpu_usage_diff = cpu_usage_total - previous_cpu_usage
            cpu_utilization = (cpu_usage_diff / time_diff) * 100
            return max(0.0, min(100.0, cpu_utilization))  # Clamp between 0-100%
            
        return 0.0

    def _calculate_memory_utilization(self, current_metrics: Dict[str, float], labels: Dict[str, str]) -> float:
        """
        Calculate memory utilization percentage if memory limit is available.
        For now, returns None as we'd need container_spec_memory_limit_bytes metric.
        """
        # This would require container_spec_memory_limit_bytes metric from cAdvisor
        # For now, return None until we can get memory limits
        return None

    async def scrape_and_transform(self) -> List[ContainerPowerMetricsCreate]:
        """Scrape cAdvisor metrics and transform to ContainerPowerMetricsCreate objects."""
        metrics_text = await self.fetch_metrics()
        logging.info("First 20 lines of cAdvisor metrics:\n" + '\n'.join(metrics_text.splitlines()[:20]))
        return self.parse_metrics(metrics_text)
