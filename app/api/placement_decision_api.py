"""
This module is for managing placement decisions.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_async_db
from app.schemas.placement_decision_schema import (
    PlacementDecisionCreate,
    PlacementDecisionResponse,
    PlacementDecisionOut,
)
from app.repositories import placement_decision
from app.utils.constants import (
    PLACEMENT_DECISION_STATUS_FAILURE,
    PLACEMENT_DECISION_STATUS_OK,
)


router = APIRouter(prefix="/placement_decisions", tags=["Placement Decisions"])


@router.post("/", response_model=PlacementDecisionResponse)
async def save_decision(
    decision: PlacementDecisionCreate,
    db: AsyncSession = Depends(get_async_db),
):
    """
    Save a placement decision
    """
    try:
        db_obj = await placement_decision.save_decision(db, decision)
        return PlacementDecisionResponse(
            decision_id=db_obj.decision_id, status=PLACEMENT_DECISION_STATUS_OK
        )
    except Exception as e:
        return PlacementDecisionResponse(
            decision_id=None, status=PLACEMENT_DECISION_STATUS_FAILURE, summary=str(e)
        )


@router.get("/{namespace}/{name}/", response_model=list[PlacementDecisionOut])
async def get_decisions(
    namespace: str, name: str, db: AsyncSession = Depends(get_async_db)
):
    """
    Get all placement decisions
    """
    return await placement_decision.get_decisions(db, namespace, name)


@router.get("/{namespace}/{name}/{decision_id}", response_model=PlacementDecisionOut)
async def get_decision(
    namespace: str,
    name: str,
    decision_id: str,
    db: AsyncSession = Depends(get_async_db),
):
    """
    Get a specific placement decision
    """
    db_obj = await placement_decision.get_decision(db, namespace, name, decision_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Decision not found")
    return db_obj
