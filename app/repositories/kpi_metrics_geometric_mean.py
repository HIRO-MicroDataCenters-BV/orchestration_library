"""
Repository module for KPI metrics.
This module contains functions to interact with the KPI metrics in the database.
"""

from typing import List
import logging
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from app.metrics.helper import record_api_metrics
from app.models.kpi_metrics_geometric_mean import KPIMetricsGeometricMean
from app.models.tuning_parameter import TuningParameter
from app.schemas.kpi_metrics_geometric_mean_schema import KPIMetricsGeometricMeanItem
from app.utils.exceptions import DatabaseConnectionException


# Configure logger
logger = logging.getLogger(__name__)


async def fetch_latest_geometric_mean_kpis(
    db_session: AsyncSession,
    kpi_geometrics_request_args: dict,
    metrics_details: dict,
) -> List[KPIMetricsGeometricMeanItem]:
    """
    Get the latest geometric mean KPI metrics entry from the database by request decision ID.

    Args:
        db_session (AsyncSession): The database session.
        kpi_geometrics_request_args (dict): The request arguments containing
            request_decision_id (UUID): The request decision ID to filter KPI metrics.
            skip (int): The number of entries to skip.
            limit (int): The number of latest entries to retrieve.
        metrics_details (dict): Details for metrics logging.


    Returns:
        List[KPIMetricsGeometricMeanItem]: The latest geometric mean KPI metrics entries.
        If request_decision_id is not provided, fetches entries based on skip and limit.
        If request_decision_id is provided, fetches entries
        for that specific request decision ID.
    """
    excep = None
    try:
        skip = kpi_geometrics_request_args.pop("skip", 0)
        limit = kpi_geometrics_request_args.pop("limit", 10)
        request_decision_id: UUID = kpi_geometrics_request_args.get(
            "request_decision_id"
        )
        if request_decision_id:
            query = select(KPIMetricsGeometricMean).where(
                KPIMetricsGeometricMean.request_decision_id == request_decision_id
            )
        else:
            query = (
                select(KPIMetricsGeometricMean)
                .order_by(KPIMetricsGeometricMean.last_seq_id.asc())
                .offset(skip)
                .limit(limit)
            )

        kpi_geometrics_result = await db_session.execute(query)
        record_api_metrics(
            metrics_details=metrics_details,
            status_code=200,
        )
        return kpi_geometrics_result.scalars().all()
    except SQLAlchemyError as e:
        excep = e
        logger.error(
            "Database error while fetching latest geometric mean KPI metrics: %s",
            str(e),
        )
        raise DatabaseConnectionException(
            "Failed to fetch latest geometric mean KPI metrics",
            details={"error": str(e)},
        ) from e
    except Exception as e:
        excep = e
        logger.error(
            "Unexpected error while fetching latest geometric mean KPI metrics: %s",
            str(e),
        )
        raise DatabaseConnectionException(
            "An unexpected error occurred while fetching latest geometric mean KPI metrics",
            details={"error": str(e)},
        ) from e
    finally:
        if excep:
            record_api_metrics(
                metrics_details=metrics_details, status_code=503, exception=excep
            )


async def get_latest_geometric_mean_kpis_tuning_parameters(
    db_session: AsyncSession, limit: int
):
    """
    Get the latest geometric mean KPI metrics entries for tuning parameters.

    Args:
        limit (int): The number of latest entries to retrieve.
    Returns:
        List of the latest geometric mean KPI metrics entries.
    """
    try:
        K = KPIMetricsGeometricMean
        P = TuningParameter

        # Subquery to get the latest tuning parameter for each KPI metric
        subquery = (
            select(P)
            .where(P.created_at <= K.last_created_at)
            .order_by(P.created_at.desc())
            .limit(1)
            .lateral()
        )

        query = (
            select(
                K.last_created_at,
                K.gm_cpu_utilization,
                K.gm_mem_utilization,
                K.gm_decision_time_in_seconds,
                K.request_decision_id,
                P.alpha,
                P.beta,
                P.gamma,
                P.output_1,
                P.output_2,
                P.output_3,
                P.created_at,
            )
            .select_from(K)
            .join(subquery, True, isouter=True)
            .order_by(K.last_created_at.desc())
            .limit(limit)
        )

        kpi_geometrics_tuning_params_result = await db_session.execute(query)
        return kpi_geometrics_tuning_params_result.all()
    except SQLAlchemyError as e:
        logger.error(
            "Database error while fetching latest geometric mean KPI metrics for tuning parameters: %s",
            str(e),
        )
        raise DatabaseConnectionException(
            "Failed to fetch latest geometric mean KPI metrics for tuning parameters",
            details={"error": str(e)},
        ) from e
    except Exception as e:
        logger.error(
            "Unexpected error while fetching latest geometric mean KPI metrics for tuning parameters: %s",
            str(e),
        )
        raise DatabaseConnectionException(
            "An unexpected error occurred while fetching latest geometric mean KPI metrics for tuning parameters",
            details={"error": str(e)},
        ) from e
