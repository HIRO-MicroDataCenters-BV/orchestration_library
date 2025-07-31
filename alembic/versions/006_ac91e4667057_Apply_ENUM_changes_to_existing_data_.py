"""Apply ENUM changes to existing data

Revision ID: ac91e4667057
Revises: 2f4fda3d071b
Create Date: 2025-07-31 16:53:47.667794

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ac91e4667057'
down_revision: Union[str, None] = '2f4fda3d071b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    """Upgrade schema."""
    #---------------------------------------------------------------
    # 1. Update all 'Swap' to 'swap_x'
    op.execute("""
        UPDATE workload_action
        SET action_type = 'swap_x'
        WHERE action_type::text = 'Swap';
    """)

    # 2. Update all action_type values to lowercase and cast to enum
    op.execute("""
        UPDATE workload_action
        SET action_type = LOWER(action_type::text)::workload_action_type_enum;
    """)

    # 3. Rename old enum
    op.execute("""
        ALTER TYPE workload_action_type_enum RENAME TO workload_action_type_enum_old;
    """)

    # 4. Create new enum without 'Swap'
    op.execute("""
        CREATE TYPE workload_action_type_enum AS ENUM (
            'bind', 'create', 'delete', 'move', 'swap_x', 'swap_y'
        );
    """)

    # 5. Alter column to use new enum
    op.execute("""
        ALTER TABLE workload_action
        ALTER COLUMN action_type TYPE workload_action_type_enum
        USING action_type::text::workload_action_type_enum;
    """)

    # 6. Drop old enum
    op.execute("DROP TYPE workload_action_type_enum_old;")
    #---------------------------------------------------------------

    #---------------------------------------------------------------
    # --- Repeat similar pattern for other enums below ---
    # Update workload_action_status_enum: change 'successful' to 'succeeded', partial to pending and remaing all lowercase
    op.execute("""
    UPDATE workload_action
    SET action_status = 
        CASE
            WHEN LOWER(action_status::text) = 'successful' THEN 'succeeded'
            WHEN LOWER(action_status::text) = 'partial' THEN 'pending'
            ELSE action_status
        END;
""")
    op.execute("""
        ALTER TYPE workload_action_status_enum RENAME TO workload_action_status_enum_old;
    """)
    op.execute("""
        CREATE TYPE workload_action_status_enum AS ENUM (
            'pending', 'succeeded', 'failed'
        );
    """)
    op.execute("""
        ALTER TABLE workload_action
        ALTER COLUMN action_status TYPE workload_action_status_enum
        USING LOWER(action_status::text)::workload_action_status_enum;
    """)
    op.execute("DROP TYPE workload_action_status_enum_old;")
    #---------------------------------------------------------------

    #---------------------------------------------------------------
    # Update workload_request_decision_status_enum: all lowercase, 'successful' to 'successful'
    op.execute("""
        ALTER TYPE workload_request_decision_status_enum RENAME TO workload_request_decision_status_enum_old;
    """)
    op.execute("""
        CREATE TYPE workload_request_decision_status_enum AS ENUM (
            'pending', 'successful', 'failed'
        );
    """)
    op.execute("""
        ALTER TABLE workload_request_decision
        ALTER COLUMN decision_status TYPE workload_request_decision_status_enum
        USING LOWER(decision_status::text)::workload_request_decision_status_enum;
    """)
    op.execute("DROP TYPE workload_request_decision_status_enum_old;")
    #---------------------------------------------------------------


    #---------------------------------------------------------------
    # Update pod_parent_type_enum: all lowercase
    op.execute("""
        ALTER TYPE pod_parent_type_enum RENAME TO pod_parent_type_enum_old;
    """)
    op.execute("""
        CREATE TYPE pod_parent_type_enum AS ENUM (
            'deployment', 'statefulset', 'replicaset', 'job', 'daemonset', 'cronjob'
        );
    """)
    op.execute("""
        ALTER TABLE workload_action
        ALTER COLUMN pod_parent_type TYPE pod_parent_type_enum
        USING LOWER(pod_parent_type::text)::pod_parent_type_enum;
    """)
    op.execute("""
        ALTER TABLE workload_request_decision
        ALTER COLUMN pod_parent_kind TYPE pod_parent_type_enum
        USING LOWER(pod_parent_kind::text)::pod_parent_type_enum;
    """)
    op.execute("DROP TYPE pod_parent_type_enum_old;")
    #---------------------------------------------------------------


def downgrade():
    """Downgrade schema."""
    # Downgrade workload_action_type_enum
    #---------------------------------------------------------------
    # 1. Rename current enum
    op.execute("""
        ALTER TYPE workload_action_type_enum RENAME TO workload_action_type_enum_new;
    """)

    # 2. Recreate old enum (with capitalized values, including 'Swap')
    op.execute("""
        CREATE TYPE workload_action_type_enum AS ENUM (
            'Bind', 'Create', 'Delete', 'Move', 'Swap', 'bind', 'create', 'delete', 'move', 'swap_x', 'swap_y'
        );
    """)

    op.execute("""
        ALTER TABLE workload_action
        ALTER COLUMN action_type TYPE workload_action_type_enum
        USING action_type::text::workload_action_type_enum;
    """)

    op.execute("""
        UPDATE workload_action
        SET action_type = (
            CASE
                WHEN LOWER(action_type::text) IN ('bind', 'create', 'delete', 'move') THEN INITCAP(action_type::text)
                WHEN LOWER(action_type::text) IN ('swap_x', 'swap_y') THEN 'Swap'
                ELSE action_type::text
            END
        )::workload_action_type_enum
        WHERE action_type IS NOT NULL;
    """)
    # 5. Drop the new enum
    op.execute("DROP TYPE workload_action_type_enum_new;")
    #---------------------------------------------------------------

    #---------------------------------------------------------------
    # Downgrade action_status_enum
    op.execute("""
        ALTER TYPE workload_action_status_enum RENAME TO workload_action_status_enum_new;
    """)
    op.execute("""
        CREATE TYPE workload_action_status_enum AS ENUM (
            'pending', 'successful', 'failed', 'partial', 'succeeded'
        );
    """)
    op.execute("""
        ALTER TABLE workload_action
        ALTER COLUMN action_status TYPE workload_action_status_enum
        USING action_status::text::workload_action_status_enum;
    """)
    op.execute("""
        UPDATE workload_action
        SET action_status = 'successful'
        WHERE action_status = 'succeeded';
    """)
    op.execute("DROP TYPE workload_action_status_enum_new;")
    #---------------------------------------------------------------

    #---------------------------------------------------------------
    # Downgrade workload_request_decision_status_enum
    op.execute("""
        ALTER TYPE workload_request_decision_status_enum RENAME TO workload_request_decision_status_enum_new;
    """)
    op.execute("""
        CREATE TYPE workload_request_decision_status_enum AS ENUM (
            'pending', 'successful', 'failed'
        );
    """)
    op.execute("""
        ALTER TABLE workload_request_decision
        ALTER COLUMN decision_status TYPE workload_request_decision_status_enum
        USING decision_status::text::workload_request_decision_status_enum;
    """)
    op.execute("DROP TYPE workload_request_decision_status_enum_new;")
    #---------------------------------------------------------------

    #---------------------------------------------------------------
    # Downgrade pod_parent_type_enum
    op.execute("""
        ALTER TYPE pod_parent_type_enum RENAME TO pod_parent_type_enum_new;
    """)
    op.execute("""
        CREATE TYPE pod_parent_type_enum AS ENUM (
            'Deployment', 'StatefulSet', 'ReplicaSet', 'Job', 'DaemonSet', 'CronJob', 
               'deployment', 'statefulset', 'replicaset', 'job', 'daemonset', 'cronjob'
        );
    """)
    op.execute("""
    ALTER TABLE workload_action
    ALTER COLUMN pod_parent_type TYPE pod_parent_type_enum
    USING
        CASE
            WHEN LOWER(pod_parent_type::text) = 'deployment' THEN 'Deployment'
            WHEN LOWER(pod_parent_type::text) = 'statefulset' THEN 'StatefulSet'
            WHEN LOWER(pod_parent_type::text) = 'replicaset' THEN 'ReplicaSet'
            WHEN LOWER(pod_parent_type::text) = 'job' THEN 'Job'
            WHEN LOWER(pod_parent_type::text) = 'daemonset' THEN 'DaemonSet'
            WHEN LOWER(pod_parent_type::text) = 'cronjob' THEN 'CronJob'
            ELSE pod_parent_type::text
        END::pod_parent_type_enum;
    """)
    op.execute("""
        ALTER TABLE workload_request_decision
        ALTER COLUMN pod_parent_kind TYPE pod_parent_type_enum
        USING
            CASE
                WHEN LOWER(pod_parent_kind::text) = 'deployment' THEN 'Deployment'
                WHEN LOWER(pod_parent_kind::text) = 'statefulset' THEN 'StatefulSet'
                WHEN LOWER(pod_parent_kind::text) = 'replicaset' THEN 'ReplicaSet'
                WHEN LOWER(pod_parent_kind::text) = 'job' THEN 'Job'
                WHEN LOWER(pod_parent_kind::text) = 'daemonset' THEN 'DaemonSet'
                WHEN LOWER(pod_parent_kind::text) = 'cronjob' THEN 'CronJob'
                ELSE pod_parent_kind::text
            END::pod_parent_type_enum;
    """)
    
    op.execute("DROP TYPE pod_parent_type_enum_new;")
    #---------------------------------------------------------------
