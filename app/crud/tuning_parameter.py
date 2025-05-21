"""
CRUD operations for managing tuning parameters in the database.
"""
from datetime import datetime
from typing import Optional, Sequence

from sqlalchemy import select, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import TuningParameter
from app.tuning_parameter_schema import TuningParameterCreate


async def create_tuning_parameter(
        db: AsyncSession, tuning_parameter: TuningParameterCreate
) -> TuningParameter:
    """
    Create a new tuning parameter in the database.

    Args:
        db (AsyncSession): Database session
        tuning_parameter (TuningParameterCreate): The tuning parameter data to create

    Returns:
        TuningParameter: The created tuning parameter object

    Note:
        This function automatically commits the transaction and refreshes the object
        to ensure all database-generated fields are populated.
    """
    db_tuning_parameter = TuningParameter(**tuning_parameter.dict())
    db.add(db_tuning_parameter)
    await db.commit()
    await db.refresh(db_tuning_parameter)
    return db_tuning_parameter


async def get_tuning_parameters(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
) -> Sequence[TuningParameter]:
    """
    Get a list of tuning parameters with pagination and optional date filtering.

    Args:
        db (AsyncSession): Database session
        skip (int): Number of records to skip (default: 0)
        limit (int): Maximum number of records to return (default: 100)
        start_date (Optional[datetime]): Filter records created after this date
        end_date (Optional[datetime]): Filter records created before this date

    Returns:
        Sequence[TuningParameter]: List of tuning parameters matching the criteria

    Note:
        If both start_date and end_date are provided, records must fall within
        the specified date range. If only one date is provided, only that
        boundary is enforced.
    """
    query = select(TuningParameter)

    if start_date or end_date:
        conditions = []
        if start_date:
            conditions.append(TuningParameter.created_at >= start_date)
        if end_date:
            conditions.append(TuningParameter.created_at <= end_date)
        if conditions:
            query = query.where(and_(*conditions))

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


async def get_latest_tuning_parameters(db: AsyncSession, limit: int = 1) -> Sequence[TuningParameter]:
    """
    Get the latest N tuning parameters based on creation time.

    Args:
        db: Database session
        limit: Number of latest parameters to return
    """
    query = select(TuningParameter).order_by(desc(TuningParameter.created_at)).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()
