"""
CRUD operations for managing tuning parameters in the database.
"""
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import TuningParameter
from app.tuning_parameter_schema import TuningParameterCreate, TuningParameterUpdate


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


async def get_tuning_parameter(
    db: AsyncSession, tuning_parameter_id: int
) -> Optional[TuningParameter]:
    """
    Get a tuning parameter by its ID.
    """
    result = await db.execute(
        select(TuningParameter).where(TuningParameter.id == tuning_parameter_id)
    )
    return result.scalar_one_or_none()


async def get_tuning_parameters(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100
) -> List[TuningParameter]:
    """
    Get a list of tuning parameters with pagination.
    """
    query = select(TuningParameter).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


async def update_tuning_parameter(
    db: AsyncSession,
    tuning_parameter_id: int,
    tuning_parameter_update: TuningParameterUpdate
) -> Optional[TuningParameter]:
    """
    Update a tuning parameter's information.
    """
    db_tuning_parameter = await get_tuning_parameter(db, tuning_parameter_id)
    if not db_tuning_parameter:
        return None
    
    update_data = tuning_parameter_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_tuning_parameter, field, value)
    
    await db.commit()
    await db.refresh(db_tuning_parameter)
    return db_tuning_parameter


async def delete_tuning_parameter(
    db: AsyncSession, tuning_parameter_id: int
) -> bool:
    """
    Delete a tuning parameter from the database.
    """
    db_tuning_parameter = await get_tuning_parameter(db, tuning_parameter_id)
    if not db_tuning_parameter:
        return False
    
    await db.delete(db_tuning_parameter)
    await db.commit()
    return True 