"""
Test API for CadvisorMetricsService
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from app.services.cadvisor_metrics_service import CadvisorMetricsService
import logging

router = APIRouter(prefix="/test/cadvisor")

@router.get("/metrics", response_model=List[Dict[str, Any]])
async def test_cadvisor_metrics():
    """
    Test endpoint to fetch and parse cAdvisor metrics directly.
    Returns the parsed container metrics without storing in database.
    """
    try:
        service = CadvisorMetricsService()
        metrics = await service.scrape_and_transform()
        
        # Convert to dict format for JSON response
        result = []
        for metric in metrics:
            result.append({
                "timestamp": metric.timestamp.isoformat(),
                "container_name": metric.container_name,
                "pod_name": metric.pod_name,
                "namespace": metric.namespace,
                "node_name": metric.node_name,
                "metric_source": metric.metric_source,
                "cpu_utilization_percent": metric.cpu_utilization_percent,
                "memory_utilization_percent": metric.memory_utilization_percent,
                "memory_usage_bytes": metric.memory_usage_bytes,
                "cpu_core_watts": metric.cpu_core_watts,
                "cpu_package_watts": metric.cpu_package_watts,
                "memory_power_watts": metric.memory_power_watts,
                "platform_watts": metric.platform_watts,
                "other_watts": metric.other_watts,
                "network_io_rate_bytes_per_sec": metric.network_io_rate_bytes_per_sec,
                "disk_io_rate_bytes_per_sec": metric.disk_io_rate_bytes_per_sec,
            })
        
        logging.info(f"CadvisorTestAPI: Retrieved {len(result)} metrics")
        return result
        
    except Exception as e:
        logging.error(f"Error testing cAdvisor metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch cAdvisor metrics: {str(e)}")

@router.get("/raw-metrics")
async def test_cadvisor_raw_metrics():
    """
    Test endpoint to fetch raw cAdvisor metrics text.
    Returns the raw Prometheus metrics format for debugging.
    """
    try:
        service = CadvisorMetricsService()
        raw_metrics = await service.fetch_metrics()
        
        # Return first 50 lines for easier viewing
        lines = raw_metrics.split('\n')
        preview_lines = lines[:50]
        
        return {
            "total_lines": len(lines),
            "preview_lines": len(preview_lines),
            "raw_metrics_preview": '\n'.join(preview_lines),
            "full_metrics_length": len(raw_metrics)
        }
        
    except Exception as e:
        logging.error(f"Error fetching raw cAdvisor metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch raw cAdvisor metrics: {str(e)}")

@router.get("/health")
async def test_cadvisor_health():
    """
    Test endpoint to check if cAdvisor is accessible.
    """
    try:
        service = CadvisorMetricsService()
        raw_metrics = await service.fetch_metrics()
        
        # Basic health check - if we can fetch metrics, cAdvisor is accessible
        lines = raw_metrics.split('\n')
        cpu_metrics_count = sum(1 for line in lines if 'container_cpu_usage_seconds_total' in line)
        memory_metrics_count = sum(1 for line in lines if 'container_memory_usage_bytes' in line)
        
        return {
            "status": "healthy",
            "cadvisor_url": service.CADVISOR_METRICS_URL,
            "total_metric_lines": len(lines),
            "cpu_metric_lines": cpu_metrics_count,
            "memory_metric_lines": memory_metrics_count,
            "raw_data_size_bytes": len(raw_metrics)
        }
        
    except Exception as e:
        logging.error(f"cAdvisor health check failed: {e}")
        return {
            "status": "unhealthy",
            "cadvisor_url": CadvisorMetricsService.CADVISOR_METRICS_URL,
            "error": str(e)
        }