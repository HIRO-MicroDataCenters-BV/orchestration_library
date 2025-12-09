"""Additional types to WorkloadActionTypeEnum

Revision ID: 89150dad1bc1
Revises: 11d18c468b34
Create Date: 2025-12-09 10:55:15.990532

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '89150dad1bc1'
down_revision: Union[str, None] = '11d18c468b34'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("ALTER TYPE workload_action_type_enum ADD VALUE IF NOT EXISTS 'scale';")
    op.execute("ALTER TYPE workload_action_type_enum ADD VALUE IF NOT EXISTS 'update_resources';")
    op.execute("ALTER TYPE workload_action_type_enum ADD VALUE IF NOT EXISTS 'redeploy';")


def downgrade() -> None:
    """Downgrade schema."""
    # 0) Drop dependent view(s) before altering enum columns
    op.execute("DROP VIEW IF EXISTS workload_decision_action_flow;")

    # 1) Rename current enum to *_old
    op.execute("ALTER TYPE workload_action_type_enum RENAME TO workload_action_type_enum_old;")

    # 2) Create a new enum with ONLY original values
    op.execute("""
        CREATE TYPE workload_action_type_enum AS ENUM (
            'bind',
            'create',
            'delete',
            'move',
            'swap_x',
            'swap_y'
        );
    """)

    # 3) Make data compatible (choose mapping for removed enum values)
    op.execute("UPDATE workload_action SET action_type = 'move' WHERE action_type = 'scale';")
    op.execute("UPDATE workload_action SET action_type = 'swap_x' WHERE action_type = 'update_resources';")
    op.execute("UPDATE workload_action SET action_type = 'delete' WHERE action_type = 'redeploy';")
    op.execute("UPDATE workload_request_decision SET action_type = 'move' WHERE action_type = 'scale';")
    op.execute("UPDATE workload_request_decision SET action_type = 'swap_x' WHERE action_type = 'update_resources';")
    op.execute("UPDATE workload_request_decision SET action_type = 'delete' WHERE action_type = 'redeploy';")
    # 4) Alter column to use the new enum type
    op.execute("""
        ALTER TABLE workload_action
        ALTER COLUMN action_type TYPE workload_action_type_enum
        USING action_type::text::workload_action_type_enum;
    """)
    op.execute("""
        ALTER TABLE workload_request_decision
        ALTER COLUMN action_type TYPE workload_action_type_enum
        USING action_type::text::workload_action_type_enum;
    """)

    # 5) Drop the old enum type
    op.execute("DROP TYPE IF EXISTS workload_action_type_enum_old;")

    # 6) Recreate the view with the original (pre-010-upgrade) definition from 010 downgrade
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

