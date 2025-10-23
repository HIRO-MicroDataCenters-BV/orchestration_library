"""
API routes for managing KPI metrics.
This module defines the API endpoints for creating KPI metrics entries in the database.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_async_db
from app.schemas.kpi_metrics_schema import (
    KPIMetricsSchema,
    KPIMetricsCreate,
)
from app.repositories.kpi_metrics import (
    create_kpi_metrics,
)
from app.utils.helper import metrics

router = APIRouter(
    prefix="/kpi_metrics", tags=["KPI Metrics"]
)


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