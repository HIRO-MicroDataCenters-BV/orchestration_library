"""
Tuning Parameter routes.
This module defines the API endpoints for managing Tuning Parameter in the database.
It includes routes for creating, retrieving, updating, and deleting Tuning Parameter records.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_db
from app.crud import tuning_parameter as tuning_parameter_crud
from app.tuning_parameter_schema import (
    TuningParameterCreate,
    TuningParameterResponse
)

router = APIRouter(prefix="/tuning_parameters")


@router.post("/", response_model=TuningParameterResponse)
async def create_tuning_parameter(
    tuning_parameter: TuningParameterCreate,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Create a new tuning parameter.
    """
    return await tuning_parameter_crud.create_tuning_parameter(db, tuning_parameter)


@router.get("/{tuning_parameter_id}", response_model=TuningParameterResponse)
async def read_tuning_parameter(
    tuning_parameter_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Get a specific tuning parameter by ID.
    """
    db_tuning_parameter = await tuning_parameter_crud.get_tuning_parameter(db, tuning_parameter_id)
    if db_tuning_parameter is None:
        raise HTTPException(status_code=404, detail="Tuning parameter not found")
    return db_tuning_parameter


@router.get("/", response_model=List[TuningParameterResponse])
async def read_tuning_parameters(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Get a list of tuning parameters with pagination.
    """
    tuning_parameters = await tuning_parameter_crud.get_tuning_parameters(db, skip=skip, limit=limit)
    return tuning_parameters


@router.delete("/{tuning_parameter_id}")
async def delete_tuning_parameter(
    tuning_parameter_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Delete a tuning parameter.
    """
    success = await tuning_parameter_crud.delete_tuning_parameter(db, tuning_parameter_id)
    if not success:
        raise HTTPException(status_code=404, detail="Tuning parameter not found")
    return {"message": f"Tuning parameter {tuning_parameter_id} has been deleted"}
