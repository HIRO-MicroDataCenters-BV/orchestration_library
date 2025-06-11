from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_async_db
from app.schemas.alerts_request import AlertCreateRequest, AlertResponse
from app.repositories import alerts as alerts_repo

router = APIRouter(prefix="/alerts")


@router.post(
    "/",
    response_model=AlertResponse,
    responses={
        status.HTTP_403_FORBIDDEN: {"description": "Not Authorized"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Internal Server Error"},
    },
)
async def create(
        data: AlertCreateRequest, db: AsyncSession = Depends(get_async_db)
):
    """
    Create a new alert.

    Args:
        data (AlertCreateRequest): The alert data to create
        db (AsyncSession): Database session dependency

    Returns:
        AlertResponse: The created alert

    Raises:
        DatabaseConnectionException: If there's a database error
    """
    return await alerts_repo.create_alert(db, data)
