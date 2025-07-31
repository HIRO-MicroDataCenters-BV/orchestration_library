"""Modify the workload action type enum

Revision ID: 2f4fda3d071b
Revises: 4e3724e12554
Create Date: 2025-07-31 15:18:14.617129

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '2f4fda3d071b'
down_revision: Union[str, None] = '4e3724e12554'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Rename the old enum type
    op.execute("ALTER TYPE action_status_enum RENAME TO workload_action_status_enum;")

    # 2. Add new value to the existing enum of action statuses
    op.execute("ALTER TYPE workload_action_status_enum ADD VALUE IF NOT EXISTS 'succeeded';")

    # 3. Add new values to the existing enum (if not already present) of workload action types
    op.execute("ALTER TYPE workload_action_type_enum ADD VALUE IF NOT EXISTS 'swap_x';")
    op.execute("ALTER TYPE workload_action_type_enum ADD VALUE IF NOT EXISTS 'swap_y';")
    op.execute("ALTER TYPE workload_action_type_enum ADD VALUE IF NOT EXISTS 'bind';")
    op.execute("ALTER TYPE workload_action_type_enum ADD VALUE IF NOT EXISTS 'create';")
    op.execute("ALTER TYPE workload_action_type_enum ADD VALUE IF NOT EXISTS 'delete';")
    op.execute("ALTER TYPE workload_action_type_enum ADD VALUE IF NOT EXISTS 'move';")

    
    # 4. Add new value to the existing enum of pod parent types
    op.execute("ALTER TYPE pod_parent_type_enum ADD VALUE IF NOT EXISTS 'deployment';")
    op.execute("ALTER TYPE pod_parent_type_enum ADD VALUE IF NOT EXISTS 'statefulset';")
    op.execute("ALTER TYPE pod_parent_type_enum ADD VALUE IF NOT EXISTS 'replicaset';")
    op.execute("ALTER TYPE pod_parent_type_enum ADD VALUE IF NOT EXISTS 'job';")
    op.execute("ALTER TYPE pod_parent_type_enum ADD VALUE IF NOT EXISTS 'daemonset';")
    op.execute("ALTER TYPE pod_parent_type_enum ADD VALUE IF NOT EXISTS 'cronjob';")


def downgrade() -> None:
    """Downgrade schema by removing the values added in upgrade.

    NOTE: You must manually specify the enum values to keep in the CREATE TYPE statement below.
    """
    #---------------------------------------------------------
    # 1. Rename the current enum type
    op.execute("ALTER TYPE workload_action_type_enum RENAME TO workload_action_type_enum_new;")

    # 2. Create the old enum type (without the values you added)
    op.execute("""
        CREATE TYPE workload_action_type_enum AS ENUM (
            'Bind', 'Create', 'Delete', 'Move', 'Swap'
        );
    """)

    # 3. Alter the column to use the recreated enum type
    op.execute("""
        ALTER TABLE workload_action
        ALTER COLUMN action_type TYPE workload_action_type_enum
        USING action_type::text::workload_action_type_enum;
    """)

    # 4. Drop the new enum type
    op.execute("DROP TYPE workload_action_type_enum_new;")
    #---------------------------------------------------------

    #---------------------------------------------------------
    # --- Repeat similar pattern for other enums below ---
    # downgrade action_status_enum: contains statuses 'pending', 'successful', 'failed'
    op.execute("""
        CREATE TYPE action_status_enum AS ENUM (
            'pending', 'successful', 'failed', 'partial'
        );
    """)
    op.execute("""
        ALTER TABLE workload_action
        ALTER COLUMN action_status TYPE action_status_enum
        USING LOWER(action_status::text)::action_status_enum;
    """)
    op.execute("DROP TYPE workload_action_status_enum;")
    #---------------------------------------------------------

    #---------------------------------------------------------
    # Downgrade pod_parent_type_enum: all values should be camel case
    op.execute("""
    UPDATE workload_action
    SET pod_parent_type = CASE
        WHEN LOWER(pod_parent_type::text) = 'deployment' THEN 'Deployment'
        WHEN LOWER(pod_parent_type::text) = 'statefulset' THEN 'StatefulSet'
        WHEN LOWER(pod_parent_type::text) = 'replicaset' THEN 'ReplicaSet'
        WHEN LOWER(pod_parent_type::text) = 'job' THEN 'Job'
        WHEN LOWER(pod_parent_type::text) = 'daemonset' THEN 'DaemonSet'
        WHEN LOWER(pod_parent_type::text) = 'cronjob' THEN 'CronJob'
        ELSE pod_parent_type
    END
    WHERE pod_parent_type IS NOT NULL;
""")
    op.execute("ALTER TYPE pod_parent_type_enum RENAME TO pod_parent_type_enum_new;")
    op.execute("""
        CREATE TYPE pod_parent_type_enum AS ENUM (
            'Deployment', 'StatefulSet', 'ReplicaSet', 'Job', 'DaemonSet', 'CronJob'
        );
    """)
    op.execute("""
        ALTER TABLE workload_action
        ALTER COLUMN pod_parent_type TYPE pod_parent_type_enum
        USING pod_parent_type::text::pod_parent_type_enum;
    """)
    op.execute("""
        ALTER TABLE workload_request_decision
        ALTER COLUMN pod_parent_kind TYPE pod_parent_type_enum
        USING pod_parent_kind::text::pod_parent_type_enum;
    """)
    op.execute("DROP TYPE pod_parent_type_enum_new;")
    #---------------------------------------------------------
