from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models import WorkloadRequest
from app.schemas import WorkloadRequestCreate


# def create_workload_request(db: Session, req: WorkloadRequestCreate):
#     obj = WorkloadRequest(**req.model_dump())
#     db.add(obj)
#     db.commit()
#     db.refresh(obj)
#     return obj

async def create_workload_request(db: AsyncSession, req: WorkloadRequestCreate):
    obj = WorkloadRequest(**req.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj

