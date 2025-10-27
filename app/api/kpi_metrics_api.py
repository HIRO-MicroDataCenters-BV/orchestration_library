"""
API routes for managing KPI metrics.
This module defines the API endpoints for creating KPI metrics entries in the database.
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_async_db
from app.schemas.kpi_metrics_schema import (
    KPIMetricsSchema,
    KPIMetricsCreate,
)
from app.repositories.kpi_metrics import (
    create_kpi_metrics,
    get_kpi_metrics,
    get_latest_kpi_metrics,
)
from app.utils.helper import metrics

router = APIRouter(prefix="/kpi_metrics", tags=["KPI Metrics"])


@router.post(path="/", response_model=KPIMetricsSchema)
async def create_kpi_metrics_route(
    data: KPIMetricsCreate,
    db_session: AsyncSession = Depends(get_async_db),
):
    """
    Create a new KPI metrics entry.

    Args:
        data (KPIMetricsCreate): The KPI metrics data to create.
        db_session (AsyncSession): Database session dependency.

    Returns:
        KPIMetricsSchema: The newly created KPI metrics entry.
    """
    return await create_kpi_metrics(
        db_session, data, metrics_details=metrics("POST", "/kpi_metrics")
    )


@router.get(path="/", response_model=List[KPIMetricsSchema])
async def get_kpi_metrics_route(
    skip: int = 0,
    limit: int = 100,
    start_datetime: Optional[datetime] = None,
    end_datetime: Optional[datetime] = None,
    db_session: AsyncSession = Depends(get_async_db),
):
    """
    Retrieve KPI metrics entries.

    Args:
        db_session (AsyncSession): Database session dependency.

    Returns:
        List[KPIMetricsSchema]: List of KPI metrics entries.
    """
    return await get_kpi_metrics(
        db_session,
        kpi_metrics_request_args={
            "skip": skip,
            "limit": limit,
            "start_datetime": start_datetime,
            "end_datetime": end_datetime,
        },
        metrics_details=metrics("GET", "/kpi_metrics"),
    )


@router.get(path="/latest", response_model=List[KPIMetricsSchema])
async def get_latest_kpi_metrics_route(
    node_name: Optional[str] = Query(None, description="Filter by node name"),
    limit: int = Query(1, description="Number of latest entries to retrieve")   ,
    db_session: AsyncSession = Depends(get_async_db),
):
    """
    Retrieve the latest KPI metrics entries for a specific node.
    Args:
        node_name (str): The name of the node to filter KPI metrics.
        limit (int): The number of latest entries to retrieve.
        db_session (AsyncSession): Database session dependency.
    Returns:
        List[KPIMetricsSchema]: List of latest KPI metrics entries for the specified node.
    """
    metrics_path = "/kpi_metrics/latest"
    if node_name:
        metrics_path += f"/?node_name={node_name}"
    metrics_path += f"&limit={limit}"
    return await get_latest_kpi_metrics(
        db_session,
        node_name=node_name,
        limit=limit,
        metrics_details=metrics("GET", metrics_path),
    )
