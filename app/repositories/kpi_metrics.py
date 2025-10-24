"""
Repository module for KPI metrics.
This module contains functions to interact with the KPI metrics in the database.
"""

from typing import List
import logging

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from app.metrics.helper import record_api_metrics
from app.models.kpi_metrics import KPIMetrics
from app.schemas.kpi_metrics_schema import (
    KPIMetricsSchema,
    KPIMetricsCreate,
)
from app.utils.exceptions import DatabaseConnectionException


# Configure logger
logger = logging.getLogger(__name__)


async def create_kpi_metrics(
    db_session: AsyncSession,
    data: KPIMetricsCreate,
    metrics_details: dict,
) -> KPIMetricsSchema:
    """
    Create a new KPI metrics entry in the database.

    Args:
        db_session (AsyncSession): The database session.
        data (KPIMetricsCreate): The KPI metrics data to create.
        metrics_details (dict): Details for metrics logging.

    Returns:
        KPIMetricsSchema: The newly created KPI metrics entry.
    """
    exception = None
    try:
        logger.debug("Creating KPI metrics with data: %s", data.model_dump())
        new_kpi_metrics = KPIMetrics(**data.model_dump())
        db_session.add(new_kpi_metrics)

        await db_session.commit()
        await db_session.refresh(new_kpi_metrics)
        logger.info(f"Created new KPI metrics entry with ID: {new_kpi_metrics.id}")
        record_api_metrics(
            metrics_details=metrics_details,
            status_code=200,
        )
        return new_kpi_metrics
    except IntegrityError as e:
        exception = e
        logger.error("Integrity error while creating KPI metrics: %s", str(e))
        await db_session.rollback()
        raise DatabaseConnectionException(
            "Invalid KPI metrics data", details={"error": str(e)}
        ) from e
    except SQLAlchemyError as e:
        exception = e
        logger.error("Database error while creating KPI metrics: %s", str(e))
        await db_session.rollback()
        raise DatabaseConnectionException(
            "Failed to create KPI metrics", details={"error": str(e)}
        ) from e
    except Exception as e:
        exception = e
        logger.error("Unexpected error while creating KPI metrics: %s", str(e))
        await db_session.rollback()
        raise DatabaseConnectionException(
            "An unexpected error occurred while creating KPI metric",
            details={"error": str(e)},
        ) from e
    finally:
        if exception:
            record_api_metrics(
                metrics_details=metrics_details, status_code=503, exception=exception
            )


async def get_kpi_metrics(
    db_session: AsyncSession, kpi_metrics_request_args: dict, metrics_details: dict
) -> List[KPIMetricsSchema]:
    """
    Get all KPI metrics from the database.

    Args:
        db_session (AsyncSession): The database session.
        kpi_metrics_request_args (dict): The filters for querying KPI metrics.
    """
    exception = None
    try:
        skip = kpi_metrics_request_args.pop("skip", 0)
        limit = kpi_metrics_request_args.pop("limit", 100)
        start_datetime = kpi_metrics_request_args.pop("start_datetime", None)
        end_datetime = kpi_metrics_request_args.pop("end_datetime", None)
        logger.debug(
            "Fetching KPI metrics with skip=%d, limit=%d, start_datetime=%s, end_datetime=%s",
            skip,
            limit,
            start_datetime,
            end_datetime,
        )
        query = select(KPIMetrics).offset(skip).limit(limit)
        conditions = []
        if start_datetime:
            conditions.append(KPIMetrics.created_at >= start_datetime)
        if end_datetime:
            conditions.append(KPIMetrics.created_at <= end_datetime)
        if conditions:
            query = query.where(and_(*conditions))
        result = await db_session.execute(query)
        record_api_metrics(
            metrics_details=metrics_details,
            status_code=200,
        )
        return result.scalars().all()
    except SQLAlchemyError as e:
        exception = e
        logger.error("Database error while fetching KPI metrics: %s", str(e))
        raise DatabaseConnectionException(
            "Failed to fetch KPI metrics", details={"error": str(e)}
        ) from e
    except Exception as e:
        exception = e
        logger.error("Unexpected error while fetching KPI metrics: %s", str(e))
        raise DatabaseConnectionException(
            "An unexpected error occurred while fetching KPI metrics",
            details={"error": str(e)},
        ) from e
    finally:
        if exception:
            record_api_metrics(
                metrics_details=metrics_details, status_code=503, exception=exception
            )


async def get_latest_kpi_metrics(
    db_session: AsyncSession, node_name: str, metrics_details: dict, limit: int = 1
) -> List[KPIMetricsSchema]:
    """
    Get the latest KPI metrics entry from the database.

    Args:
        db_session (AsyncSession): The database session.
        node_name (str): The name of the node to filter KPI metrics.
        metrics_details (dict): Details for metrics logging.
        limit (int): The number of latest entries to retrieve.

    Returns:
        List[KPIMetricsSchema]: The latest KPI metrics entries.
    """
    exception = None
    try:
        safe_limit = max(1, limit)
        if node_name:
            # Latest rows for a specific node
            query = (
                select(KPIMetrics)
                .where(KPIMetrics.node_name == node_name)
                .order_by(KPIMetrics.created_at.desc())
                .limit(safe_limit)
            )
        else:
            logger.warning(
                "Node name not provided. Fetching latest KPI metrics for all nodes."
            )
            # Window function to get latest row per node
            subq = select(
                KPIMetrics.id,
                KPIMetrics.node_name,
                KPIMetrics.cpu_utilization,
                KPIMetrics.mem_utilization,
                KPIMetrics.decision_time_in_seconds,
                KPIMetrics.created_at,
                func.row_number()
                .over(
                    partition_by=KPIMetrics.node_name,
                    order_by=KPIMetrics.created_at.desc(),
                )
                .label("rn"),
            ).subquery()
            query = (
                select(KPIMetrics)
                .join(subq, KPIMetrics.id == subq.c.id)
                .where(subq.c.rn <= safe_limit)
                .order_by(KPIMetrics.node_name.asc(), KPIMetrics.created_at.desc())
            )

        result = await db_session.execute(query)
        record_api_metrics(
            metrics_details=metrics_details,
            status_code=200,
        )
        return result.scalars().all()
    except SQLAlchemyError as e:
        exception = e
        logger.error("Database error while fetching latest KPI metrics: %s", str(e))
        raise DatabaseConnectionException(
            "Failed to fetch latest KPI metrics", details={"error": str(e)}
        ) from e
    except Exception as e:
        exception = e
        logger.error("Unexpected error while fetching latest KPI metrics: %s", str(e))
        raise DatabaseConnectionException(
            "An unexpected error occurred while fetching latest KPI metrics",
            details={"error": str(e)},
        ) from e
    finally:
        if exception:
            record_api_metrics(
                metrics_details=metrics_details, status_code=503, exception=exception
            )
