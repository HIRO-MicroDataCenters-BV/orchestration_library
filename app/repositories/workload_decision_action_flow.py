"""
This module provides a function to retrieve the scheduling decision and
action taken for each pod.
It joins the `WorkloadRequestDecision` and `WorkloadAction` models based
on pod name, namespace, and node name.
The function supports optional filtering by pod name, namespace, and node name.
It returns a sequence of dictionaries containing the decision and action details.
It also handles database errors and logs them appropriately.
"""

from typing import Sequence
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from app.models.workload_decision_action_flow_view import WorkloadDecisionActionFlowView
from app.utils.constants import WorkloadActionTypeEnum
from app.utils.exceptions import (
    DatabaseConnectionException,
)

logger = logging.getLogger(__name__)


async def get_workload_decision_action_flow(
    db: AsyncSession,
    pod_name: str = None,
    namespace: str = None,
    node_name: str = None,
    action_type: WorkloadActionTypeEnum = None,
    skip: int = 0,
    limit: int = 100,
) -> Sequence[WorkloadDecisionActionFlowView]:
    try:
        pod_filters = []
        if pod_name:
            pod_filters.append(
                WorkloadDecisionActionFlowView.decision_pod_name == pod_name
            )
        if namespace:
            pod_filters.append(
                WorkloadDecisionActionFlowView.decision_namespace == namespace
            )
        if node_name:
            pod_filters.append(
                WorkloadDecisionActionFlowView.decision_node_name == node_name
            )
        if action_type == WorkloadActionTypeEnum.BIND:
            if pod_name:
                pod_filters.append(
                    WorkloadDecisionActionFlowView.bound_pod_name == pod_name
                )
            if namespace:
                pod_filters.append(
                    WorkloadDecisionActionFlowView.bound_pod_namespace == namespace
                )
            if node_name:
                pod_filters.append(
                    WorkloadDecisionActionFlowView.bound_node_name == node_name
                )
        elif action_type == WorkloadActionTypeEnum.DELETE:
            if pod_name:
                pod_filters.append(
                    WorkloadDecisionActionFlowView.deleted_pod_name == pod_name
                )
            if namespace:
                pod_filters.append(
                    WorkloadDecisionActionFlowView.deleted_pod_namespace == namespace
                )
            if node_name:
                pod_filters.append(
                    WorkloadDecisionActionFlowView.deleted_node_name == node_name
                )
        elif (
            action_type == WorkloadActionTypeEnum.CREATE
            or action_type == WorkloadActionTypeEnum.MOVE
            or action_type == WorkloadActionTypeEnum.SWAP_X
            or action_type == WorkloadActionTypeEnum.SWAP_Y
        ):
            if pod_name:
                pod_filters.append(
                    WorkloadDecisionActionFlowView.created_pod_name == pod_name
                )
            if namespace:
                pod_filters.append(
                    WorkloadDecisionActionFlowView.created_pod_namespace == namespace
                )
            if node_name:
                pod_filters.append(
                    WorkloadDecisionActionFlowView.created_node_name == node_name
                )

        if pod_filters and len(pod_filters) > 0:
            stmt = (
                select(WorkloadDecisionActionFlowView)
                .where(*pod_filters)
                .offset(skip)
                .limit(limit)
            )
        else:
            stmt = select(WorkloadDecisionActionFlowView).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()
    except SQLAlchemyError as e:
        logger.error(
            "Database error while getting workload decision action flow list: %s",
            str(e),
        )
        raise DatabaseConnectionException(
            "Failed to get workload decision action flow list",
            details={"error": str(e)},
        ) from e
