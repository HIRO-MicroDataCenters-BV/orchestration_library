#from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from .models import WorkloadRequest, WorkloadRequestDecision
from .schemas import WorkloadRequestCreate, WorkloadRequestDecisionCreate

def create_workload_request(db: Session, req: WorkloadRequestCreate):
    obj = WorkloadRequest(**req.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def create_workload_request_decision(db: Session, decision: WorkloadRequestDecisionCreate):
    obj = WorkloadRequestDecision(**decision.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj
