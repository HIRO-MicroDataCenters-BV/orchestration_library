"""
Schemas for tuning parameters.
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class TuningParameterBase(BaseModel):
    """
    Base schema for Tuning Parameter
    """
    output_1: float
    output_2: float
    output_3: float
    alpha: float
    beta: float
    gamma: float


class TuningParameterCreate(TuningParameterBase):
    """
    Schema for creating a tuning parameter
    """
    pass


class TuningParameterUpdate(BaseModel):
    """
    Schema for updating a tuning parameter
    """
    output_1: Optional[float] = None
    output_2: Optional[float] = None
    output_3: Optional[float] = None
    alpha: Optional[float] = None
    beta: Optional[float] = None
    gamma: Optional[float] = None


class TuningParameterResponse(TuningParameterBase):
    """
    Schema for tuning parameter response
    """
    id: int
    created_at: datetime

    class Config:
        orm_mode = True