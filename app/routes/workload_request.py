from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db, get_async_db
from app import schemas, crud

router = APIRouter(prefix="/workload_request")

# @router.post("/")
# def create(data: schemas.WorkloadRequestCreate, db: Session = Depends(get_db)):
#     return crud.create_workload_request(db, data)

@router.post("/")
async def create(data: schemas.WorkloadRequestCreate, db: AsyncSession = Depends(get_async_db)):
    return await crud.create_workload_request(db, data)

