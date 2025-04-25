from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db, get_async_db
from sqlalchemy.ext.asyncio import AsyncSession
from app import schemas, crud

router = APIRouter(prefix="/workload_request_decision")

# @router.post("/")
# def create(data: schemas.WorkloadRequestDecisionCreate, db: Session = Depends(get_db)):
#     return crud.create_workload_request_decision(db, data)

@router.post("/")
async def create(data: schemas.WorkloadRequestDecisionCreate, db: AsyncSession = Depends(get_async_db)):
    return await crud.create_workload_request_decision(db, data)

