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

from app.metrics.helper import record_workload_decision_action_flow_metrics
from app.models.workload_decision_action_flow_view import WorkloadDecisionActionFlowView
from app.utils.constants import WorkloadActionTypeEnum
from app.utils.exceptions import (
    DatabaseConnectionException,
)

logger = logging.getLogger(__name__)


def _add_initial_filters(pod_flow_filters, flow_filters):
    if flow_filters.get("decision_id"):
        pod_flow_filters.append(
            WorkloadDecisionActionFlowView.decision_id == flow_filters["decision_id"]
        )
    if flow_filters.get("action_id"):
        pod_flow_filters.append(
            WorkloadDecisionActionFlowView.action_id == flow_filters["action_id"]
        )
    if flow_filters.get("pod_name"):
        pod_flow_filters.append(
            WorkloadDecisionActionFlowView.decision_pod_name == flow_filters["pod_name"]
        )
    if flow_filters.get("namespace"):
        pod_flow_filters.append(
            WorkloadDecisionActionFlowView.decision_namespace
            == flow_filters["namespace"]
        )
    if flow_filters.get("node_name"):
        pod_flow_filters.append(
            WorkloadDecisionActionFlowView.decision_node_name
            == flow_filters["node_name"]
        )
    if flow_filters.get("action_type"):
        pod_flow_filters.append(
            WorkloadDecisionActionFlowView.action_type == flow_filters["action_type"]
        )


def _add_bind_filters(pod_flow_filters, pod_name, namespace, node_name):
    if pod_name:
        pod_flow_filters.append(
            WorkloadDecisionActionFlowView.bound_pod_name == pod_name
        )
    if namespace:
        pod_flow_filters.append(
            WorkloadDecisionActionFlowView.bound_pod_namespace == namespace
        )
    if node_name:
        pod_flow_filters.append(
            WorkloadDecisionActionFlowView.bound_node_name == node_name
        )


def _add_delete_swap_filters(pod_flow_filters, pod_name, namespace, node_name):
    if pod_name:
        pod_flow_filters.append(
            WorkloadDecisionActionFlowView.deleted_pod_name == pod_name
        )
    if namespace:
        pod_flow_filters.append(
            WorkloadDecisionActionFlowView.deleted_pod_namespace == namespace
        )
    if node_name:
        pod_flow_filters.append(
            WorkloadDecisionActionFlowView.deleted_node_name == node_name
        )


def _add_move_filters(pod_flow_filters, pod_name, namespace, node_name):
    if pod_name:
        pod_flow_filters.append(
            WorkloadDecisionActionFlowView.deleted_pod_name == pod_name
        )
    if namespace:
        pod_flow_filters.append(
            WorkloadDecisionActionFlowView.deleted_pod_namespace == namespace
        )
    if node_name:
        pod_flow_filters.append(
            WorkloadDecisionActionFlowView.created_node_name == node_name
        )


def _add_create_filters(pod_flow_filters, pod_name, namespace, node_name):
    if pod_name:
        pod_flow_filters.append(
            WorkloadDecisionActionFlowView.created_pod_name == pod_name
        )
    if namespace:
        pod_flow_filters.append(
            WorkloadDecisionActionFlowView.created_pod_namespace == namespace
        )
    if node_name:
        pod_flow_filters.append(
            WorkloadDecisionActionFlowView.created_node_name == node_name
        )


def _build_pod_flow_filters(flow_filters: dict) -> list:
    """Build SQLAlchemy filters based on provided flow_filters."""
    pod_name = flow_filters.get("pod_name")
    namespace = flow_filters.get("namespace")
    node_name = flow_filters.get("node_name")
    action_type = flow_filters.get("action_type")
    pod_flow_filters = []
    _add_initial_filters(pod_flow_filters, flow_filters)
    if action_type == WorkloadActionTypeEnum.BIND:
        _add_bind_filters(pod_flow_filters, pod_name, namespace, node_name)
    elif action_type == WorkloadActionTypeEnum.CREATE:
        _add_create_filters(pod_flow_filters, pod_name, namespace, node_name)
    elif action_type == WorkloadActionTypeEnum.MOVE:
        _add_move_filters(pod_flow_filters, pod_name, namespace, node_name)
    elif action_type in (
        WorkloadActionTypeEnum.DELETE,
        WorkloadActionTypeEnum.SWAP_X,
        WorkloadActionTypeEnum.SWAP_Y,
    ):
        _add_delete_swap_filters(pod_flow_filters, pod_name, namespace, node_name)
    return pod_flow_filters


async def get_workload_decision_action_flow(
    db: AsyncSession, flow_filters: dict, metrics_details: dict
) -> Sequence[WorkloadDecisionActionFlowView]:
    """
    Get the workload decision action flow for the specified filters.
    Full list if not filters.
    """
    exception = None
    try:
        skip = flow_filters.get("skip", 0)
        limit = flow_filters.get("limit", 100)
        pod_flow_filters = _build_pod_flow_filters(flow_filters)
        if pod_flow_filters:
            stmt = (
                select(WorkloadDecisionActionFlowView)
                .where(*pod_flow_filters)
                .offset(skip)
                .limit(limit)
                .order_by(WorkloadDecisionActionFlowView.decision_created_at.desc())
            )
        else:
            stmt = (
                select(WorkloadDecisionActionFlowView)
                .offset(skip)
                .limit(limit)
                .order_by(WorkloadDecisionActionFlowView.decision_created_at.desc())
            )
        result = await db.execute(stmt)
        record_workload_decision_action_flow_metrics(
            metrics_details=metrics_details,
            status_code=200,
        )
        return result.scalars().all()
    except SQLAlchemyError as e:
        exception = e
        logger.error(
            "Database error while getting workload decision action flow list: %s",
            str(e),
        )
        raise DatabaseConnectionException(
            "Failed to get workload decision action flow list",
            details={"error": str(e)},
        ) from e
    finally:
        if exception:
            record_workload_decision_action_flow_metrics(
                metrics_details=metrics_details, status_code=500, exception=exception
            )
