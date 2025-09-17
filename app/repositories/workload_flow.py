"""
This module provides a function to retrieve the scheduling decision and 
action taken for each pod.
It joins the `WorkloadRequestDecision` and `WorkloadAction` models based 
on pod name, namespace, and node name.
The function supports optional filtering by pod name, namespace, and node name.
It returns a sequence of dictionaries containing the decision and action details.
It also handles database errors and logs them appropriately.
"""

from typing import Any, Optional, Sequence, Dict
import logging

from sqlalchemy import and_, join, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from app.models.workload_action import WorkloadAction
from app.models.workload_request_decision import WorkloadRequestDecision
from app.utils.constants import WorkloadActionTypeEnum
from app.utils.exceptions import (
    DatabaseConnectionException,
)

logger = logging.getLogger(__name__)


async def get_workload_decision_action_flow(
    db: AsyncSession, pod_name: str, namespace: str, node_name: str, action_type: WorkloadActionTypeEnum
) -> Sequence[Dict[str, Any]]:
    """
    Retrieves the scheduling decision and action taken for each pod.
    """
    try:
        join_conditions = [WorkloadRequestDecision.action_type == WorkloadAction.action_type]
        if action_type == WorkloadActionTypeEnum.BIND:
            join_conditions.extend([
                WorkloadRequestDecision.pod_name == WorkloadAction.bound_pod_name,
                WorkloadRequestDecision.namespace == WorkloadAction.bound_pod_namespace,
                WorkloadRequestDecision.node_name == WorkloadAction.bound_node_name,
            ])
        elif action_type == WorkloadActionTypeEnum.CREATE or \
                action_type == WorkloadActionTypeEnum.MOVE or \
                action_type == WorkloadActionTypeEnum.SWAP_X or \
                action_type == WorkloadActionTypeEnum.SWAP_Y:
            join_conditions.extend([
                WorkloadRequestDecision.pod_name == WorkloadAction.created_node_name,
                WorkloadRequestDecision.namespace == WorkloadAction.created_pod_namespace,
                WorkloadRequestDecision.node_name == WorkloadAction.created_node_name,
            ])
        elif action_type == WorkloadActionTypeEnum.DELETE:
            join_conditions.extend([
                WorkloadRequestDecision.pod_name == WorkloadAction.deleted_pod_name,
                WorkloadRequestDecision.namespace == WorkloadAction.deleted_pod_namespace,
                WorkloadRequestDecision.node_name == WorkloadAction.deleted_node_name,
            ])

        # Build join condition
        j = join(
            WorkloadRequestDecision,
            WorkloadAction,
            and_(
                *join_conditions
            ),
        )

        # Build filters if provided
        filters = []
        if action_type:
            filters.append(WorkloadRequestDecision.action_type == action_type)
        if pod_name:
            filters.append(WorkloadRequestDecision.pod_name == pod_name)
        if namespace:
            filters.append(WorkloadRequestDecision.namespace == namespace)
        if node_name:
            filters.append(WorkloadRequestDecision.node_name == node_name)

        stmt = select(WorkloadRequestDecision, WorkloadAction).select_from(j)

        if filters:
            stmt = stmt.where(and_(*filters))

        result = await db.execute(stmt)
        rows = result.all()

        # Return as list of dicts
        return [{"decision": row[0].to_dict(), "action": row[1].to_dict()} for row in rows]
    except SQLAlchemyError as e:
        logger.error(
            "Database error while getting workload decison action flow: %s", str(e)
        )
        raise DatabaseConnectionException(
            "Failed to get workload decison action flow", details={"error": str(e)}
        ) from e
