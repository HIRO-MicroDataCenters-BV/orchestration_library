"""
API endpoints for node power metrics.
"""

from fastapi import APIRouter, HTTPException
from typing import List, Optional
from app.services.unified_node_metrics_service import UnifiedNodeMetricsService
import logging

router = APIRouter(prefix="/api/node-power-metrics", tags=["node-power-metrics"])

@router.get("/latest")
async def get_latest_node_metrics(
    node_name: Optional[str] = None,
    limit: int = 100
):
    """Get latest node power metrics"""
    try:
        service = UnifiedNodeMetricsService()
        metrics = await service.get_latest_metrics(node_name=node_name, limit=limit)
        return {"metrics": metrics, "count": len(metrics)}
    except Exception as e:
        logging.error(f"Error retrieving node metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve node metrics")

@router.post("/collect")
async def collect_node_metrics():
    """Manually trigger node metrics collection"""
    try:
        service = UnifiedNodeMetricsService()
        stored_count = await service.collect_and_store_metrics()
        return {"message": f"Successfully collected and stored {stored_count} node metrics"}
    except Exception as e:
        logging.error(f"Error collecting node metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to collect node metrics")