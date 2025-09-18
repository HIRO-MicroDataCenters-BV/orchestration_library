"""API endpoint to retrieve workload decision and action flow for pods."""

from typing import Optional, Sequence
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_async_db
from app.repositories.workload_decision_action_flow import (
    get_workload_decision_action_flow,
)
from app.schemas.workload_decision_action_flow_schema import (
    WorkloadDecisionActionFlowItem
)
from app.utils.constants import WorkloadActionTypeEnum


router = APIRouter(
    prefix="/workload_decision_action_flow", tags=["Workload Decision Action Flow"]
)


@router.get("/", response_model=Sequence[WorkloadDecisionActionFlowItem])
async def workload_decision_action_flow(
    db: AsyncSession = Depends(get_async_db),
    pod_name: Optional[str] = None,
    namespace: Optional[str] = None,
    node_name: Optional[str] = None,
    action_type: Optional[WorkloadActionTypeEnum] = None,
    skip: int = 0,
    limit: int = 100,
):
    """
    Get list of workload decision and action flows with pagination.
    Args:
        pod_name (str, optional): Filter by pod name.
        namespace (str, optional): Filter by namespace.
        node_name (str, optional): Filter by node name.
        action_type (WorkloadActionTypeEnum, optional): Filter by action type.
        skip (int): Number of records to skip (default: 0)
        limit (int): Maximum number of records to return (default: 100)
        db (AsyncSession, optional): Database session dependency.
            Defaults to Depends(get_async_db).
    Returns:
        List[WorkloadDecisionActionFlow]
            A sequence of dictionaries containing the WorkloadDecisionActionFlow details.
    Raises:
        DatabaseConnectionException: If there is an error connecting to the database.
    """
    return await get_workload_decision_action_flow(
        db,
        pod_name=pod_name,
        namespace=namespace,
        node_name=node_name,
        action_type=action_type,
        skip=skip,
        limit=limit,
    )


# @router.get("/", response_model=Sequence[Dict[str, Any]])
# async def workload_decision_action_flow(
#     pod_name: str,
#     namespace: str,
#     node_name: str,
#     action_type: WorkloadActionTypeEnum,
#     db: AsyncSession = Depends(get_async_db),
# ):
#     """
#     Retrieve the decision and action flow for a specific pod.
#     This endpoint returns a list of dictionaries containing the decision and action details
#     for the given pod, namespace, node, and action type.
#     Args:
#         pod_name (str): Name of the pod to retrieve.
#         namespace (str): Namespace of the pod.
#         node_name (str): Name of the node.
#         action_type (WorkloadActionTypeEnum): Type of action to filter by.
#         db (AsyncSession): Database session dependency.
#     Returns:
#         Sequence[WorkloadDecisionActionFlow]: List of WorkloadDecisionActionFlow details for the specified pod.
#     Raises:
#         DatabaseConnectionException: If there is a database connection error.
#     """
#     return await get_workload_decision_action_flow(
#         db, pod_name, namespace, node_name, action_type
#     )
