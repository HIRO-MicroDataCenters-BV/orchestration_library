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


def _add_bind_filters(pod_filters, pod_name, namespace, node_name):
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

def _add_delete_filters(pod_filters, pod_name, namespace, node_name):
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

def _add_create_move_swap_filters(pod_filters, pod_name, namespace, node_name):
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

def _build_pod_filters(flow_filters: dict) -> list:
    pod_name = flow_filters.get("pod_name")
    namespace = flow_filters.get("namespace")
    node_name = flow_filters.get("node_name")
    action_type = flow_filters.get("action_type")
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
        _add_bind_filters(pod_filters, pod_name, namespace, node_name)
    elif action_type == WorkloadActionTypeEnum.DELETE:
        _add_delete_filters(pod_filters, pod_name, namespace, node_name)
    elif action_type in (
        WorkloadActionTypeEnum.CREATE,
        WorkloadActionTypeEnum.MOVE,
        WorkloadActionTypeEnum.SWAP_X,
        WorkloadActionTypeEnum.SWAP_Y,
    ):
        _add_create_move_swap_filters(pod_filters, pod_name, namespace, node_name)
    return pod_filters

async def get_workload_decision_action_flow(
    db: AsyncSession,
    flow_filters: dict = None,
    skip: int = 0,
    limit: int = 100,
) -> Sequence[WorkloadDecisionActionFlowView]:
    """
    Get the workload decision action flow for the specified filters. 
    Full list if not filters.
    """
    try:
        flow_filters = flow_filters or {}
        pod_filters = _build_pod_filters(flow_filters)
        if pod_filters:
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
