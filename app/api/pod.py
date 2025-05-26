"""
DB pod routes.
This module defines the API endpoints for managing pods in the database.
It includes routes for creating, retrieving, updating, and deleting pod records.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_async_db
from app.schemas.pod import PodCreate, PodUpdate
from app.repositories import pod

router = APIRouter(prefix="/db_pod")


@router.post("/")
async def create(data: PodCreate, db: AsyncSession = Depends(get_async_db)):
    """
    Create a new pod.
    """
    return await pod.create_pod(db, data)


@router.get("/")
async def get(db: AsyncSession = Depends(get_async_db)):
    """
    Retrieve pods based on various filters. If no filters are provided,
    return all pods.
    """
    return await pod.get_pod(db)


@router.get("/{pod_id}")
async def get_by_id(pod_id: int, db: AsyncSession = Depends(get_async_db)):
    """
    Retrieve a pod by its ID.
    """
    return await pod.get_pod(db, pod_id)

@router.put("/{pod_id}")
async def update(
    pod_id: int, data: PodUpdate, db: AsyncSession = Depends(get_async_db)
):
    """
    Update a pod by its ID.
    """
    return await pod.update_pod(db, pod_id, data)


@router.delete("/{pod_id}")
async def delete(pod_id: int, db: AsyncSession = Depends(get_async_db)):
    """
    Delete a pod by its ID.
    """
    return await pod.delete_pod(db, pod_id)
