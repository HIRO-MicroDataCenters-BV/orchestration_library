"""
Container power metrics API endpoints.
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_async_db
from app.repositories.container_power_metrics import ContainerPowerMetricsRepository
from app.schemas.container_power_metrics import (
    ContainerPowerMetricsCreate,
    ContainerPowerMetricsUpdate,
    ContainerPowerMetricsResponse,
)

router = APIRouter(prefix="/api/v1/container-power-metrics")

@router.post("/", response_model=ContainerPowerMetricsResponse)
async def create_metrics(
    metrics: ContainerPowerMetricsCreate,
    db: AsyncSession = Depends(get_async_db)
) -> ContainerPowerMetricsResponse:
    repository = ContainerPowerMetricsRepository(db)
    return await repository.create(metrics)

@router.get("/", response_model=List[ContainerPowerMetricsResponse])
async def list_metrics(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    container_name: Optional[str] = None,
    pod_name: Optional[str] = None,
    namespace: Optional[str] = None,
    node_name: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    db: AsyncSession = Depends(get_async_db)
) -> List[ContainerPowerMetricsResponse]:
    repository = ContainerPowerMetricsRepository(db)
    return await repository.get_all(
        skip=skip,
        limit=limit,
        container_name=container_name,
        pod_name=pod_name,
        namespace=namespace,
        node_name=node_name,
        start_time=start_time,
        end_time=end_time
    )

@router.get("/pk/", response_model=ContainerPowerMetricsResponse)
async def get_metrics_by_pk(
    timestamp: datetime = Query(..., description="Timestamp (RFC3339)"),
    container_name: str = Query(...),
    pod_name: str = Query(...),
    db: AsyncSession = Depends(get_async_db)
) -> ContainerPowerMetricsResponse:
    repository = ContainerPowerMetricsRepository(db)
    metrics = await repository.get_by_pk(timestamp, container_name, pod_name)
    if not metrics:
        raise HTTPException(status_code=404, detail="Metrics not found")
    return metrics

@router.put("/pk/", response_model=ContainerPowerMetricsResponse)
async def update_metrics(
    timestamp: datetime = Query(..., description="Timestamp (RFC3339)"),
    container_name: str = Query(...),
    pod_name: str = Query(...),
    metrics_update: ContainerPowerMetricsUpdate = ...,
    db: AsyncSession = Depends(get_async_db)
) -> ContainerPowerMetricsResponse:
    repository = ContainerPowerMetricsRepository(db)
    metrics = await repository.update(timestamp, container_name, pod_name, metrics_update)
    if not metrics:
        raise HTTPException(status_code=404, detail="Metrics not found")
    return metrics

@router.delete("/pk/")
async def delete_metrics(
    timestamp: datetime = Query(..., description="Timestamp (RFC3339)"),
    container_name: str = Query(...),
    pod_name: str = Query(...),
    db: AsyncSession = Depends(get_async_db)
) -> dict:
    repository = ContainerPowerMetricsRepository(db)
    deleted = await repository.delete(timestamp, container_name, pod_name)
    if not deleted:
        raise HTTPException(status_code=404, detail="Metrics not found")
    return {"message": "Metrics deleted successfully"}

@router.get("/container/{container_name}", response_model=List[ContainerPowerMetricsResponse])
async def get_metrics_by_container(
    container_name: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_async_db)
) -> List[ContainerPowerMetricsResponse]:
    repository = ContainerPowerMetricsRepository(db)
    return await repository.get_by_container_name(container_name, skip, limit)

@router.get("/pod/{namespace}/{pod_name}", response_model=List[ContainerPowerMetricsResponse])
async def get_metrics_by_pod(
    namespace: str,
    pod_name: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_async_db)
) -> List[ContainerPowerMetricsResponse]:
    repository = ContainerPowerMetricsRepository(db)
    return await repository.get_by_pod(pod_name, namespace, skip, limit) 