from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_async_db
from app.schemas.alerts_request import AlertCreateRequest
from app.repositories import alerts as alerts_repo

router = APIRouter(prefix="/alerts")


@router.post("/")
async def create(
        data: AlertCreateRequest, db: AsyncSession = Depends(get_async_db)
):
    """
    Create a new workload request.
    """

    return alerts_repo.create_alert(db, data)
