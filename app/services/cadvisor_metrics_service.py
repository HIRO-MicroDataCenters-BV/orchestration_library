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
        }

        # Extract metrics for each pattern
        for metric_type, pattern in metric_patterns.items():
            for match in re.finditer(pattern, metrics_text):
                labels_str, value = match.groups()
                labels = dict(re.findall(r'(\w+)="([^"]*)"', labels_str))

                # Skip metrics without container id or system containers
                container_id_path = labels.get("id", "")
                ## container_id="/kubepods/burstable/pod31f1fe79-2afd-456a-8a34-8b389fad4d50/125d3c83ffeb47e5ce06c478ef5cffd8e572d748fdefdf2a1d02ffe39439be0e"
                if not container_id_path or container_id_path.startswith("/system"):
                    continue

                # Extract actual container ID (last part after final /)
                container_id = container_id_path.split("/")[-1] if "/" in container_id_path else container_id_path
                
                # Filter for specific container ID only
                if container_id != "248680a72041fe702eb8b0357cb64ebc6d5f73fffe6fe6d4838e07e1e7345e26":
                    continue

                # Parse pod name and namespace from name label
                # Format: k8s_{CONTAINER_TYPE}_{POD_NAME}_{NAMESPACE}_{POD_UID}_{RESTART_COUNT}
                # Example: 'k8s_storage-provisioner_storage-provisioner_kube-system_07b8d242-0e7e-489b-912c-790154094378_1'
                name_label = labels.get("name", "")
                pod_name = "unknown"
                namespace = "default"

                if name_label.startswith("k8s_"):
                    name_parts = name_label.split("_")
                    if len(name_parts) >= 4:
                        # k8s_CONTAINER_TYPE_POD_NAME_NAMESPACE_POD_UID_RESTART_COUNT
                        pod_name = name_parts[2]  # POD_NAME is at index 2
                        namespace = name_parts[3]  # NAMESPACE is at index 3

                # Fallback to direct label values if name parsing fails
                if pod_name == "unknown":
                    pod_name = labels.get("pod_name", labels.get("pod", "unknown"))
                if namespace == "default":
                    namespace = labels.get("namespace", "default")

                # Store the metric value and labels
                if container_id not in container_metrics:
                    container_metrics[container_id] = {
                        'pod_name': pod_name, 
                        'namespace': namespace,
                        'labels': labels,
                        'metrics': {}
                    }
                
                # Store both CPU and memory metrics
                container_metrics[container_id]['metrics'][metric_type] = float(value)

        # Convert to ContainerPowerMetricsCreate objects
        results = []
        current_time = datetime.utcnow()

        for container_id, data in container_metrics.items():
            labels = data['labels']
            metrics = data['metrics']
            pod_name = data['pod_name']
            namespace = data['namespace']

            # Use container_id for tracking previous metrics
            previous_data = self._previous_metrics.get(container_id)

            # Calculate CPU utilization percentage
            cpu_utilization_percent = self._calculate_cpu_utilization(metrics, previous_data)

            # Get memory usage in bytes
            memory_usage_bytes = int(metrics.get('memory_usage_bytes', 0))

            # Calculate memory utilization percentage (would need memory limits from cAdvisor)
            memory_utilization_percent = self._calculate_memory_utilization(metrics, labels)

            # Store current metrics for next calculation using container_id
            self._previous_metrics[container_id] = {
                'timestamp': current_time,
                'metrics': metrics.copy()
            }

            # Use the extracted container ID as container name
            # or fallback to cleaned name from labels
            container_name = container_id if container_id else labels.get("name", "").lstrip("/")

            results.append(ContainerPowerMetricsCreate(
                timestamp=current_time,
                container_name=container_name,
                container_id=container_id,
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
        print(results)
        logging.info(f"CadvisorMetricsService: Parsed {len(results)} container metrics from cAdvisor.")
        return results

    def _calculate_cpu_utilization(self, current_metrics: Dict[str, float], previous_data: Dict[str, Any]) -> float:
        """
        Calculate CPU utilization percentage from cpu_usage_seconds_total.
        CPU utilization = (delta_cpu_seconds / delta_time_seconds) * 100
        """
        cpu_usage_total = current_metrics.get('cpu_usage_seconds_total', 0)

        if not previous_data or 'cpu_usage_seconds_total' not in previous_data['metrics']:
            logging.debug(f"No previous CPU data - first measurement. Current: {cpu_usage_total}")
            return 0.0

        previous_cpu_usage = previous_data['metrics']['cpu_usage_seconds_total']
        time_diff = (datetime.utcnow() - previous_data['timestamp']).total_seconds()

        if time_diff > 0:
            cpu_usage_diff = cpu_usage_total - previous_cpu_usage
            cpu_utilization = (cpu_usage_diff / time_diff) * 100
            
            logging.info(f"CPU calculation: current={cpu_usage_total:.6f}, previous={previous_cpu_usage:.6f}, "
                        f"diff={cpu_usage_diff:.6f}, time={time_diff:.2f}s, utilization={cpu_utilization:.2f}%")
            
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
        logging.info("First 2 lines of cAdvisor metrics:\n" + '\n'.join(metrics_text.splitlines()[:2]))
        return self.parse_metrics(metrics_text)
