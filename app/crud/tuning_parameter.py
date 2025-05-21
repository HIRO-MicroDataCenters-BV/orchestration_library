"""
CRUD operations for managing tuning parameters in the database.
"""
from datetime import datetime
from typing import List, Optional, Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc

from app.models import TuningParameter
from app.tuning_parameter_schema import TuningParameterCreate


async def create_tuning_parameter(
        db: AsyncSession, tuning_parameter: TuningParameterCreate
) -> TuningParameter:
    """
    Create a new tuning parameter in the database.
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
    Get a list of tuning parameters with pagination and date filtering.

    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        start_date: Filter records created after this date
        end_date: Filter records created before this date
    """
    query = select(TuningParameter)

    # Apply date filters if provided
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
