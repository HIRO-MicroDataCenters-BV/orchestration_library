"""
Test API for CadvisorMetricsService
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from datetime import datetime
from app.services.cadvisor_metrics_service import CadvisorMetricsService
from app.services.kepler_metrics_service import KeplerMetricsService
from app.services.unified_container_metrics_service import UnifiedContainerMetricsService
import logging

router = APIRouter(prefix="/test")

# Shared service instances to persist previous metrics between API calls
_shared_cadvisor_service = CadvisorMetricsService()
_shared_kepler_service = KeplerMetricsService()
_shared_unified_service = UnifiedContainerMetricsService()

@router.get("/cadvisor/metrics", response_model=List[Dict[str, Any]])
async def test_cadvisor_metrics():
    """
    Test endpoint to fetch and parse cAdvisor metrics directly.
    Returns the parsed container metrics without storing in database.
    """
    try:
        metrics = await _shared_cadvisor_service.scrape_and_transform()
        
        # Convert to dict format for JSON response
        result = []
        for metric in metrics:
            result.append({
                "timestamp": metric.timestamp.isoformat(),
                "container_name": metric.container_name,
                "container_id": metric.container_id,
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

@router.get("/cadvisor/raw-metrics")
async def test_cadvisor_raw_metrics():
    """
    Test endpoint to fetch raw cAdvisor metrics text.
    Returns the raw Prometheus metrics format for debugging.
    """
    try:
        raw_metrics = await _shared_cadvisor_service.fetch_metrics()
        
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

@router.get("/cadvisor/health")
async def test_cadvisor_health():
    """
    Test endpoint to check if cAdvisor is accessible.
    """
    try:
        raw_metrics = await _shared_cadvisor_service.fetch_metrics()
        
        # Basic health check - if we can fetch metrics, cAdvisor is accessible
        lines = raw_metrics.split('\n')
        cpu_metrics_count = sum(1 for line in lines if 'container_cpu_usage_seconds_total' in line)
        memory_metrics_count = sum(1 for line in lines if 'container_memory_usage_bytes' in line)
        
        return {
            "status": "healthy",
            "cadvisor_url": _shared_cadvisor_service.CADVISOR_METRICS_URL,
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

@router.get("/cadvisor/cpu-debug")
async def test_cpu_utilization():
    """
    Test endpoint to debug CPU utilization calculation.
    Call this endpoint twice with a few seconds gap to see CPU calculation.
    """
    try:
        metrics = await _shared_cadvisor_service.scrape_and_transform()
        
        # Return info about previous metrics stored
        previous_count = len(_shared_cadvisor_service._previous_metrics)
        
        result = {
            "total_containers": len(metrics),
            "previous_metrics_stored": previous_count,
            "containers": []
        }
        
        for metric in metrics[:5]:  # Show first 5 containers
            result["containers"].append({
                "container_name": metric.container_name,
                "pod_name": metric.pod_name,
                "namespace": metric.namespace,
                "cpu_utilization_percent": metric.cpu_utilization_percent,
                "memory_usage_bytes": metric.memory_usage_bytes,
                "has_previous_data": metric.container_name in _shared_cadvisor_service._previous_metrics
            })
        
        return result
        
    except Exception as e:
        logging.error(f"CPU debug test failed: {e}")
        raise HTTPException(status_code=500, detail=f"CPU debug failed: {str(e)}")

@router.get("/cadvisor/previous-metrics")
async def get_previous_metrics():
    """
    Check what previous metrics are stored in the service.
    """
    previous_metrics = _shared_cadvisor_service._previous_metrics
    
    result = {
        "total_stored": len(previous_metrics),
        "container_ids": list(previous_metrics.keys())[:10],  # Show first 10
        "sample_data": {}
    }
    
    # Show detailed data for first container if any exist
    if previous_metrics:
        first_container_id = list(previous_metrics.keys())[0]
        result["sample_data"] = {
            "container_id": first_container_id,
            "timestamp": previous_metrics[first_container_id]["timestamp"].isoformat(),
            "metrics": previous_metrics[first_container_id]["metrics"]
        }
    
    return result


# Kepler test endpoints
@router.get("/kepler/metrics", response_model=List[Dict[str, Any]])
async def test_kepler_metrics():
    """
    Test endpoint to fetch and parse Kepler metrics directly.
    Returns the parsed container power metrics without storing in database.
    """
    try:
        metrics = await _shared_kepler_service.scrape_and_transform()
        
        # Convert to dict format for JSON response
        result = []
        for metric in metrics:
            result.append({
                "timestamp": metric.timestamp.isoformat(),
                "container_name": metric.container_name,
                "container_id": metric.container_id,
                "pod_name": metric.pod_name,
                "namespace": metric.namespace,
                "node_name": metric.node_name,
                "metric_source": metric.metric_source,
                "cpu_core_watts": metric.cpu_core_watts,
                "cpu_package_watts": metric.cpu_package_watts,
                "memory_power_watts": metric.memory_power_watts,
                "platform_watts": metric.platform_watts,
                "other_watts": metric.other_watts,
                "cpu_utilization_percent": metric.cpu_utilization_percent,
                "memory_utilization_percent": metric.memory_utilization_percent,
                "memory_usage_bytes": metric.memory_usage_bytes,
                "network_io_rate_bytes_per_sec": metric.network_io_rate_bytes_per_sec,
                "disk_io_rate_bytes_per_sec": metric.disk_io_rate_bytes_per_sec,
            })
        
        logging.info(f"KeplerTestAPI: Retrieved {len(result)} metrics")
        return result
        
    except Exception as e:
        logging.error(f"Error testing Kepler metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch Kepler metrics: {str(e)}")


@router.get("/kepler/raw-metrics")
async def test_kepler_raw_metrics():
    """
    Test endpoint to fetch raw Kepler metrics text.
    Returns the raw Prometheus metrics format for debugging.
    """
    try:
        raw_metrics = await _shared_kepler_service.fetch_metrics()
        
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
        logging.error(f"Error fetching raw Kepler metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch raw Kepler metrics: {str(e)}")


@router.get("/kepler/health")
async def test_kepler_health():
    """
    Test endpoint to check if Kepler is accessible.
    """
    try:
        raw_metrics = await _shared_kepler_service.fetch_metrics()
        
        # Basic health check - if we can fetch metrics, Kepler is accessible
        lines = raw_metrics.split('\n')
        core_joules_count = sum(1 for line in lines if 'kepler_container_core_joules_total' in line)
        package_joules_count = sum(1 for line in lines if 'kepler_container_package_joules_total' in line)
        dram_joules_count = sum(1 for line in lines if 'kepler_container_dram_joules_total' in line)
        
        return {
            "status": "healthy",
            "kepler_url": _shared_kepler_service.KEPLER_METRICS_URL,
            "total_metric_lines": len(lines),
            "core_joules_lines": core_joules_count,
            "package_joules_lines": package_joules_count,
            "dram_joules_lines": dram_joules_count,
            "raw_data_size_bytes": len(raw_metrics)
        }
        
    except Exception as e:
        logging.error(f"Kepler health check failed: {e}")
        return {
            "status": "unhealthy",
            "kepler_url": KeplerMetricsService.KEPLER_METRICS_URL,
            "error": str(e)
        }


@router.get("/kepler/power-debug")
async def test_power_calculation():
    """
    Test endpoint to debug power calculation from Kepler.
    Call this endpoint twice with a few seconds gap to see power calculation from joules.
    """
    try:
        metrics = await _shared_kepler_service.scrape_and_transform()
        
        # Return info about previous metrics stored
        previous_count = len(_shared_kepler_service._previous_metrics)
        
        result = {
            "total_containers": len(metrics),
            "previous_metrics_stored": previous_count,
            "containers": []
        }
        
        for metric in metrics[:5]:  # Show first 5 containers
            result["containers"].append({
                "container_name": metric.container_name,
                "pod_name": metric.pod_name,
                "namespace": metric.namespace,
                "cpu_core_watts": metric.cpu_core_watts,
                "cpu_package_watts": metric.cpu_package_watts,
                "memory_power_watts": metric.memory_power_watts,
                "platform_watts": metric.platform_watts,
                "other_watts": metric.other_watts,
                "container_id": f"{metric.container_name}_{metric.pod_name}_{metric.namespace}",
                "has_previous_data": f"{metric.container_name}_{metric.pod_name}_{metric.namespace}" in _shared_kepler_service._previous_metrics
            })
        
        return result
        
    except Exception as e:
        logging.error(f"Power debug test failed: {e}")
        raise HTTPException(status_code=500, detail=f"Power debug failed: {str(e)}")


@router.get("/kepler/previous-metrics")
async def get_kepler_previous_metrics():
    """
    Check what previous Kepler metrics are stored in the service.
    """
    previous_metrics = _shared_kepler_service._previous_metrics
    
    result = {
        "total_stored": len(previous_metrics),
        "container_ids": list(previous_metrics.keys())[:10],  # Show first 10
        "sample_data": {}
    }
    
    # Show detailed data for first container if any exist
    if previous_metrics:
        first_container_id = list(previous_metrics.keys())[0]
        result["sample_data"] = {
            "container_id": first_container_id,
            "timestamp": previous_metrics[first_container_id]["timestamp"].isoformat(),
            "metrics": previous_metrics[first_container_id]["metrics"]
        }
    
    return result


@router.get("/both/metrics", response_model=List[Dict[str, Any]])
async def test_both_metrics():
    """
    Test endpoint to fetch both cAdvisor and Kepler metrics and combine them.
    """
    try:
        cadvisor_metrics = await _shared_cadvisor_service.scrape_and_transform()
        kepler_metrics = await _shared_kepler_service.scrape_and_transform()
        
        result = {
            "cadvisor": [],
            "kepler": [],
            "summary": {
                "cadvisor_count": len(cadvisor_metrics),
                "kepler_count": len(kepler_metrics),
                "total_count": len(cadvisor_metrics) + len(kepler_metrics)
            }
        }
        
        # Convert cAdvisor metrics
        for metric in cadvisor_metrics:
            result["cadvisor"].append({
                "timestamp": metric.timestamp.isoformat(),
                "container_name": metric.container_name,
                "container_id": metric.container_id,
                "pod_name": metric.pod_name,
                "namespace": metric.namespace,
                "metric_source": metric.metric_source,
                "cpu_utilization_percent": metric.cpu_utilization_percent,
                "memory_utilization_percent": metric.memory_utilization_percent,
                "memory_usage_bytes": metric.memory_usage_bytes,
            })
        
        # Convert Kepler metrics
        for metric in kepler_metrics:
            result["kepler"].append({
                "timestamp": metric.timestamp.isoformat(),
                "container_name": metric.container_name,
                "container_id": metric.container_id,
                "pod_name": metric.pod_name,
                "namespace": metric.namespace,
                "metric_source": metric.metric_source,
                "cpu_core_watts": metric.cpu_core_watts,
                "cpu_package_watts": metric.cpu_package_watts,
                "memory_power_watts": metric.memory_power_watts,
                "platform_watts": metric.platform_watts,
                "other_watts": metric.other_watts,
            })
        
        logging.info(f"BothTestAPI: Retrieved {len(cadvisor_metrics)} cAdvisor + {len(kepler_metrics)} Kepler metrics")
        return result
        
    except Exception as e:
        logging.error(f"Error testing both metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch both metrics: {str(e)}")


@router.get("/health")
async def test_overall_health():
    """
    Test endpoint to check if both cAdvisor and Kepler are accessible.
    """
    cadvisor_status = "unknown"
    kepler_status = "unknown"
    
    # Test cAdvisor
    try:
        await _shared_cadvisor_service.fetch_metrics()
        cadvisor_status = "healthy"
    except Exception as e:
        cadvisor_status = f"unhealthy: {str(e)}"
    
    # Test Kepler
    try:
        await _shared_kepler_service.fetch_metrics()
        kepler_status = "healthy"
    except Exception as e:
        kepler_status = f"unhealthy: {str(e)}"
    
    return {
        "cadvisor": {
            "status": cadvisor_status,
            "url": _shared_cadvisor_service.CADVISOR_METRICS_URL
        },
        "kepler": {
            "status": kepler_status,
            "url": _shared_kepler_service.KEPLER_METRICS_URL
        },
        "overall_status": "healthy" if "healthy" in cadvisor_status and "healthy" in kepler_status else "partial"
    }


# Unified service test endpoints
@router.get("/unified/collect-and-store")
async def test_collect_and_store_metrics():
    """
    Test endpoint to run collect_and_store_metrics function.
    This will collect from both cAdvisor and Kepler, merge them, and store in database.
    Returns the number of records stored and processing details.
    """
    try:
        logging.info("Starting collect_and_store_metrics test...")
        
        # Run the collect and store process
        stored_count = await _shared_unified_service.collect_and_store_metrics()
        
        result = {
            "status": "success",
            "stored_records": stored_count,
            "message": f"Successfully processed and stored {stored_count} unified container metrics",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logging.info(f"UnifiedTestAPI: {result['message']}")
        return result
        
    except Exception as e:
        logging.error(f"Error in collect_and_store_metrics test: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to collect and store metrics: {str(e)}")


@router.get("/unified/latest-metrics")
async def test_get_latest_metrics(
    container_name: str = None,
    pod_name: str = None,
    namespace: str = None,
    limit: int = 10
):
    """
    Test endpoint to retrieve latest unified metrics from database.
    Optional filters: container_name, pod_name, namespace
    """
    try:
        metrics = await _shared_unified_service.get_latest_metrics(
            container_name=container_name,
            pod_name=pod_name,
            namespace=namespace,
            limit=limit
        )
        
        result = {
            "status": "success",
            "count": len(metrics),
            "filters": {
                "container_name": container_name,
                "pod_name": pod_name,
                "namespace": namespace,
                "limit": limit
            },
            "metrics": metrics
        }
        
        logging.info(f"UnifiedTestAPI: Retrieved {len(metrics)} metrics from database")
        return result
        
    except Exception as e:
        logging.error(f"Error retrieving latest metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve metrics: {str(e)}")


@router.get("/unified/debug-merge")
async def test_debug_merge_process():
    """
    Test endpoint to debug the merge process without storing to database.
    Shows raw metrics from both sources and the merged result.
    """
    try:
        # Collect metrics from both sources
        cadvisor_metrics = await _shared_unified_service.cadvisor_service.scrape_and_transform()
        kepler_metrics = await _shared_unified_service.kepler_service.scrape_and_transform()
        
        # Merge them (but don't store)
        unified_metrics = _shared_unified_service._merge_metrics(cadvisor_metrics, kepler_metrics)
        
        result = {
            "status": "success",
            "cadvisor": {
                "count": len(cadvisor_metrics),
                "sample": [
                    {
                        "container_name": m.container_name,
                        "pod_name": m.pod_name,
                        "namespace": m.namespace,
                        "cpu_utilization_percent": m.cpu_utilization_percent,
                        "memory_usage_bytes": m.memory_usage_bytes,
                        "metric_source": m.metric_source
                    } for m in cadvisor_metrics[:3]  # Show first 3
                ]
            },
            "kepler": {
                "count": len(kepler_metrics),
                "sample": [
                    {
                        "container_name": m.container_name,
                        "pod_name": m.pod_name,
                        "namespace": m.namespace,
                        "cpu_core_watts": m.cpu_core_watts,
                        "cpu_package_watts": m.cpu_package_watts,
                        "memory_power_watts": m.memory_power_watts,
                        "metric_source": m.metric_source
                    } for m in kepler_metrics[:3]  # Show first 3
                ]
            },
            "unified": {
                "count": len(unified_metrics),
                "sample": [
                    {
                        "container_name": m.container_name,
                        "pod_name": m.pod_name,
                        "namespace": m.namespace,
                        "cpu_utilization_percent": m.cpu_utilization_percent,
                        "memory_usage_bytes": m.memory_usage_bytes,
                        "cpu_core_watts": m.cpu_core_watts,
                        "cpu_package_watts": m.cpu_package_watts,
                        "memory_power_watts": m.memory_power_watts,
                        "metric_source": m.metric_source
                    } for m in unified_metrics[:3]  # Show first 3
                ]
            }
        }
        
        logging.info(f"UnifiedTestAPI: Debug merge - cAdvisor:{len(cadvisor_metrics)}, Kepler:{len(kepler_metrics)}, Unified:{len(unified_metrics)}")
        return result
        
    except Exception as e:
        logging.error(f"Error in debug merge process: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to debug merge process: {str(e)}")