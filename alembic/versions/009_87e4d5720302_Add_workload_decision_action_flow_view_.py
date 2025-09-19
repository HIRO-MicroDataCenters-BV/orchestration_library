"""Add workload_decision_action_flow view

Revision ID: 87e4d5720302
Revises: cef3654218e2
Create Date: 2025-09-17 23:22:21.963120

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '87e4d5720302'
down_revision: Union[str, None] = 'cef3654218e2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
    CREATE OR REPLACE VIEW workload_decision_action_flow AS
    SELECT
        d.id AS decision_id,
        a.id AS action_id,
        d.action_type AS action_type,
        d.pod_name AS decision_pod_name,
        d.namespace AS decision_namespace,
        d.node_name AS decision_node_name,
        a.created_pod_name,
        a.created_pod_namespace,
        a.created_node_name,
        a.deleted_pod_name,
        a.deleted_pod_namespace,
        a.deleted_node_name,
        a.bound_pod_name,
        a.bound_pod_namespace,
        a.bound_node_name,
        d.decision_status,
        a.action_status,
        d.decision_start_time,
        d.decision_end_time,
        a.action_start_time,
        a.action_end_time,
        (d.decision_end_time - d.decision_start_time) AS decision_duration,
        (a.action_end_time - a.action_start_time) AS action_duration,
        (d.decision_end_time - d.decision_start_time) + (a.action_end_time - a.action_start_time) AS total_duration,
        d.created_at AS decision_created_at,
        d.deleted_at AS decision_deleted_at,
        a.created_at AS action_created_at,
        a.updated_at AS action_updated_at,
        d.is_elastic,
        d.queue_name,
        d.demand_cpu,
        d.demand_memory,
        d.demand_slack_cpu,
        d.demand_slack_memory,
        d.pod_parent_id AS decision_pod_parent_id,
        d.pod_parent_name AS decision_pod_parent_name,
        d.pod_parent_kind AS decision_pod_parent_kind,
        a.pod_parent_name AS action_pod_parent_name,
        a.pod_parent_type AS action_pod_parent_type,
        a.pod_parent_uid AS action_pod_parent_uid,
        a.action_reason
    FROM workload_request_decision d
    JOIN workload_action a
      ON d.action_type = a.action_type
     AND (
           (d.action_type = 'bind'
            AND d.pod_name = a.bound_pod_name
            AND d.namespace = a.bound_pod_namespace
            AND d.node_name = a.bound_node_name)
        OR (d.action_type IN ('create','move','swap_x','swap_y')
            AND d.pod_name = a.created_pod_name
            AND d.namespace = a.created_pod_namespace
            AND d.node_name = a.created_node_name)
        OR (d.action_type = 'delete'
            AND d.pod_name = a.deleted_pod_name
            AND d.namespace = a.deleted_pod_namespace
            AND d.node_name = a.deleted_node_name)
     );
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP VIEW IF EXISTS workload_decision_action_flow;")
