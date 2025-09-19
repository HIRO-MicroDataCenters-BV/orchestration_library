"""
Repository for Placement Decision
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.placement_decision import PlacementDecision
from app.schemas.placement_decision_schema import PlacementDecisionCreate


async def save_decision(db: AsyncSession, decision: PlacementDecisionCreate):
    """
    Save a Placement Decision
    """
    try:
        db_obj = PlacementDecision(
            name=decision.id.name,
            namespace=decision.id.namespace,
            spec=decision.spec,
            decision_placement_lst=decision.decision.get("placement", []),
            decision_reason=decision.decision.get("reason", "Unknown"),
            trace=decision.trace,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    except Exception as e:
        await db.rollback()
        raise e


async def get_decisions(db: AsyncSession, namespace: str, name: str):
    """
    Get all Placement Decisions
    """
    stmt = select(PlacementDecision).where(
        PlacementDecision.name == name,
        PlacementDecision.namespace == namespace
    ).order_by(PlacementDecision.timestamp.desc())
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_decision(db: AsyncSession, namespace: str, name: str, decision_id: str):
    """
    Get a single Placement Decision
    """
    stmt = select(PlacementDecision).where(
        PlacementDecision.namespace == namespace,
        PlacementDecision.name == name,
        PlacementDecision.decision_id == decision_id
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
