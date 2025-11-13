"""
API routes for managing KPI metrics.
This module defines the API endpoints for creating KPI metrics entries in the database.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from requests import get
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_async_db
from app.repositories.kpi_metrics_geometric_mean import fetch_latest_geometric_mean_kpis
from app.schemas.kpi_metrics_geometric_mean_schema import KPIMetricsGeometricMeanItem
from app.schemas.kpi_metrics_schema import (
    KPIMetricsSchema,
    KPIMetricsCreate,
)
from app.repositories.kpi_metrics import (
    create_kpi_metrics,
    get_kpi_metrics,
    get_latest_kpi_metrics_by_nodes,
    get_latest_kpi_metrics_by_request_decision_ids,
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
    limit: int = 10,
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


@router.get(path="/latest_by_node", response_model=List[KPIMetricsSchema])
async def get_latest_kpi_metrics_route(
    node_name: Optional[str] = Query(None, description="Filter by node name"),
    limit: int = Query(1, description="Number of latest entries to retrieve"),
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
    metrics_path = "/kpi_metrics/latest_by_node"
    if node_name:
        metrics_path += f"/?node_name={node_name}"
    metrics_path += f"&limit={limit}"
    return await get_latest_kpi_metrics_by_nodes(
        db_session,
        node_name=node_name,
        limit=limit,
        metrics_details=metrics("GET", metrics_path),
    )


@router.get(path="/latest_by_request", response_model=List[KPIMetricsSchema])
async def get_latest_kpi_metrics_by_request_route(
    request_decision_id: Optional[UUID] = Query(
        None, description="Filter by request decision ID"
    ),
    limit: int = Query(1, description="Number of latest entries to retrieve"),
    db_session: AsyncSession = Depends(get_async_db),
):
    """
    Retrieve the latest KPI metrics entries for a specific request decision ID.

    Args:
        request_decision_id (str): The ID of the request decision to filter KPI metrics.
        limit (int): The number of latest entries to retrieve.
        db_session (AsyncSession): Database session dependency.

    Returns:
        List[KPIMetricsSchema]:
            List of latest KPI metrics entries for the specified request decision ID.
    """
    metrics_path = "/kpi_metrics/latest_by_request"
    if request_decision_id:
        metrics_path += f"/?request_decision_id={request_decision_id}"
    metrics_path += f"&limit={limit}"
    return await get_latest_kpi_metrics_by_request_decision_ids(
        db_session,
        request_decision_id=request_decision_id,
        limit=limit,
        metrics_details=metrics("GET", metrics_path),
    )


@router.get(path="/latest_geometric_mean", response_model=List[KPIMetricsGeometricMeanItem])
async def get_latest_geometric_mean_kpi_metrics_route(
    request_decision_id: Optional[UUID] = Query(
        None, description="Filter by request decision ID"
    ),
    skip: int = Query(0, description="Number of entries to skip"),
    limit: int = Query(10, description="Number of latest entries to retrieve"),
    db_session: AsyncSession = Depends(get_async_db),
):
    """
    Retrieve the latest geometric mean KPI metrics entries for a specific request decision ID.

    Args:
        request_decision_id (str): The ID of the request decision to filter KPI metrics.
        skip (int): The number of entries to skip.
        limit (int): The number of latest entries to retrieve.
        db_session (AsyncSession): Database session dependency.
    Returns:
        List[KPIMetricsSchema]:
            List of latest geometric mean KPI metrics entries for the specified request decision ID.
            or
            List of latest geometric mean KPI metrics entries based on skip and limit if
            request_decision_id is not provided.
    """
    metrics_path = "/kpi_metrics/latest_geometric_mean"
    if request_decision_id:
        metrics_path += f"/?request_decision_id={request_decision_id}"
    metrics_path += f"&limit={limit}"
    return await fetch_latest_geometric_mean_kpis(
        db_session,
        kpi_geometrics_request_args={
            "request_decision_id": request_decision_id,
            "skip": skip,
            "limit": limit,
        },
        metrics_details=metrics("GET", metrics_path),
    )
