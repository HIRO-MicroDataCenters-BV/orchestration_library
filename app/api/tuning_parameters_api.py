"""
Tuning Parameter API routes.
This module defines the API endpoints for managing Tuning Parameter in the database.
It includes routes for creating, retrieving Tuning Parameter records.
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from starlette import status

from app.repositories import tuning_parameter as tuning_parameter_crud
from app.db.database import get_async_db
from app.schemas.tuning_parameter_schema import TuningParameterCreate, TuningParameterResponse
from app.utils.exceptions import (
    DatabaseEntryNotFoundException,
    DatabaseConnectionException,
)

router = APIRouter(prefix="/tuning_parameters")


@router.post(
    "/",
    response_model=TuningParameterResponse,
    responses={
        status.HTTP_403_FORBIDDEN: {"description": "Not Authorized"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Internal Server Error"},
    },
)
async def create_tuning_parameter(
    tuning_parameter: TuningParameterCreate, db: AsyncSession = Depends(get_async_db)
):
    """
    Create a new tuning parameter.

    Args:
        tuning_parameter (TuningParameterCreate): The tuning parameter data to create
        db (AsyncSession): Database session dependency

    Returns:
        TuningParameterResponse: The created tuning parameter

    Raises:
        TuningParameterValidationError: If the input data is invalid
        TuningParameterDatabaseError: If there's a database error
    """
    try:
        return await tuning_parameter_crud.create_tuning_parameter(db, tuning_parameter)
    except SQLAlchemyError as e:
        raise DatabaseConnectionException(
            "Failed to create tuning parameter", details={"error": str(e)}
        ) from e


@router.get("/", response_model=List[TuningParameterResponse])
async def read_tuning_parameters(
    skip: int = 0,
    limit: int = 100,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: AsyncSession = Depends(get_async_db),
):
    """
    Get a list of tuning parameters with pagination and date filtering.

    Args:
        skip: Number of records to skip (default: 0)
        limit: Maximum number of records to return (default: 100)
        start_date: Filter records created after this date (optional)
        end_date: Filter records created before this date (optional)
        db (AsyncSession): Database session dependency

    Returns:
        List[TuningParameterResponse]: List of tuning parameters

    Raises:
        TuningParameterDatabaseError: If there's a database error
    """
    try:
        tuning_parameters = await tuning_parameter_crud.get_tuning_parameters(
            db, skip=skip, limit=limit, start_date=start_date, end_date=end_date
        )
        return tuning_parameters
    except SQLAlchemyError as e:
        raise DatabaseConnectionException(
            "Failed to retrieve tuning parameters", details={"error": str(e)}
        ) from e


@router.get("/latest/{limit}", response_model=List[TuningParameterResponse])
async def get_latest_tuning_parameters(
    limit: int, db: AsyncSession = Depends(get_async_db)
):
    """
    Get the latest N tuning parameters based on creation time.

    Args:
        limit (int): Number of latest parameters to return
        db (AsyncSession): Database session dependency

    Returns:
        List[TuningParameterResponse]: List of the N most recent tuning parameters

    Raises:
        TuningParameterNotFoundError: If no tuning parameters are found
        TuningParameterDatabaseError: If there's a database error
    """
    try:
        latest_parameters = await tuning_parameter_crud.get_latest_tuning_parameters(
            db, limit=limit
        )
        return latest_parameters
    except SQLAlchemyError as e:
        raise DatabaseConnectionException(
            "Failed to retrieve latest tuning parameters", details={"error": str(e)}
        ) from e
