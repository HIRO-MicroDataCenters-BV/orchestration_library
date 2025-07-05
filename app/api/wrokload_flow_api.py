"""API endpoint to retrieve workload decision and action flow for pods."""
from typing import Any, Dict, Sequence
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_async_db
from app.repositories.workload_flow import get_workload_decision_action_flow

router = APIRouter(prefix="/workload_flow", tags=["Workload Flow"])

@router.get("/", response_model=Sequence[Dict[str, Any]])
async def get_workload_flow(
    pod_name: str,
    namespace: str,
    node_name: str = None,
    db: AsyncSession = Depends(get_async_db),
):
    """
    Retrieve the scheduling decision and action taken for each pod.
    This endpoint returns a list of dictionaries containing the 
    decision and action for each pod.
    It supports optional filtering by pod name, namespace, and node name.
    If no filters are provided, it returns all pods.
    Args:
        pod_name (str): The name of the pod to filter by.
        namespace (str): The namespace of the pod to filter by.
        node_name (str, optional): The name of the node to filter by. Defaults to None.
        db (AsyncSession, optional): Database session dependency. 
            Defaults to Depends(get_async_db).
    Returns:
        Sequence[Dict[str, Any]]: 
            A sequence of dictionaries containing the decision and action details.
    Raises:
        DatabaseConnectionException: If there is an error connecting to the database.
    """
    return await get_workload_decision_action_flow(
        db, pod_name, namespace, node_name
    )
