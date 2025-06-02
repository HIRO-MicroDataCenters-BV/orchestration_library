"""
Common API endpoints 
"""

from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_async_db
from app.repositories import pod

router = APIRouter(prefix="/workload_request_per_node")


@router.get("/{node_id}")
async def get_workloads_per_pod(
    node_id: UUID, db: AsyncSession = Depends(get_async_db)
):
    """
    Retrieve workload request IDs associated with a specific node.
    Args:
        node_id (UUID): The ID of the node to retrieve workload requests for.
        db (AsyncSession): Database session dependency.
    Returns:
        list[UUID]: A list of workload request IDs associated with the node.
    """
    return await pod.workload_request_ids_per_node(db, node_id)
