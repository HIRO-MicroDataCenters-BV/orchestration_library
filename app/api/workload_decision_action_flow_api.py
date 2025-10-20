"""API endpoint to retrieve workload decision and action flow for pods."""

import time
from typing import Sequence
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_async_db
from app.repositories.workload_decision_action_flow import (
    get_workload_decision_action_flow,
)
from app.schemas.workload_decision_action_flow_schema import (
    FlowQueryParams,
    WorkloadDecisionActionFlowItem
)


router = APIRouter(
    prefix="/workload_decision_action_flow", tags=["Workload Decision Action Flow"]
)

@router.get("/", response_model=Sequence[WorkloadDecisionActionFlowItem])
async def workload_decision_action_flow(
    db: AsyncSession = Depends(get_async_db),
    flow_params: FlowQueryParams = Depends(),
    skip: int = 0,
    limit: int = 100
):
    """
    Get list of workload decision and action flows with pagination.
    Args:
        decision_id (UUID, optional): Filter by decision ID.
        action_id (UUID, optional): Filter by action ID.
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
    metrics_details = {
        "start_time": time.time(),
        "method": "GET",
        "endpoint": "/workload_decision_action_flow",
    }
    return await get_workload_decision_action_flow(
        db,
        flow_filters={
            "decision_id": flow_params.decision_id,
            "action_id": flow_params.action_id,
            "pod_name": flow_params.pod_name,
            "namespace": flow_params.namespace,
            "node_name": flow_params.node_name,
            "action_type": flow_params.action_type,
            "skip": skip,
            "limit": limit,
        },
        metrics_details=metrics_details
    )
