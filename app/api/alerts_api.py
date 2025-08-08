"""
Alert API routes.
This module defines the API endpoints for managing Alert in the database.
It includes routes for creating, retrieving Alert records.
"""

import time
from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_async_db
from app.schemas.alerts_request import AlertCreateRequest, AlertResponse
from app.repositories import alerts as alerts_repo

router = APIRouter(prefix="/alerts")


@router.post(
    "/",
    response_model=AlertResponse,
    responses={
        status.HTTP_403_FORBIDDEN: {"description": "Not Authorized"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Internal Server Error"},
    },
)
async def create(
        data: AlertCreateRequest, db: AsyncSession = Depends(get_async_db)
):
    """
    Create a new alert.

    Args:
        data (AlertCreateRequest): The alert data to create
        db (AsyncSession): Database session dependency

    Returns:
        AlertResponse: The created alert

    Raises:
        DBEntryCreationException: If there's an error creating the alert
        DataBaseException: If there's a database error
    """
    metrics_details = {
        "start_time": time.time(),
        "method": "POST",
        "endpoint": "/alerts",
    }
    return await alerts_repo.create_alert(db, data, metrics_details=metrics_details)


@router.get(
    "/",
    response_model=List[AlertResponse],
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Internal Server Error"},
    },
)
async def read_alerts(
        skip: int = 0,
        limit: int = 100,
        db: AsyncSession = Depends(get_async_db),
):
    """
    Get a list of alerts with pagination.

    Args:
        skip (int): Number of records to skip (default: 0)
        limit (int): Maximum number of records to return (default: 100)
        db (AsyncSession): Database session dependency

    Returns:
        List[AlertResponse]: List of alerts

    Raises:
        DataBaseException: If there's a database error
    """
    metrics_details = {
        "start_time": time.time(),
        "method": "GET",
        "endpoint": "/alerts",
    }
    return await alerts_repo.get_alerts(db, skip=skip, limit=limit, metrics_details=metrics_details)
