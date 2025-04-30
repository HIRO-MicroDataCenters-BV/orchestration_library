from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from orchestrationAPI.database import get_async_db
from orchestrationAPI import schemas, crud
from orchestrationAPI.schemas import PodCreate, PodUpdate

router = APIRouter(prefix="/pod")

@router.post("/")
async def create(data: PodCreate, db: AsyncSession = Depends(get_async_db)):
    return await crud.create_pod(db, data)

@router.get("/")
async def get(db: AsyncSession = Depends(get_async_db)):
    return await crud.get_pod(db)

@router.get("/{pod_id}")
async def get(pod_id: int, db: AsyncSession = Depends(get_async_db)):
    return await crud.get_pod(db, pod_id)

@router.put("/{pod_id}")
async def update(pod_id: int, data: PodUpdate, db: AsyncSession = Depends(get_async_db)):
    return await crud.update_pod(db, pod_id, data)

@router.delete("/{pod_id}")
async def delete(pod_id: int, db: AsyncSession = Depends(get_async_db)):
    return await crud.delete_pod(db, pod_id)