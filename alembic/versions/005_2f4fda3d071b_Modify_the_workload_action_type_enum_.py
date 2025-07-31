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
    #-----------------------------------------------------------------------
    # 1. Rename the current enum
    op.execute("""
        ALTER TYPE workload_action_type_enum RENAME TO workload_action_type_enum_old;
    """)
    # 2. Create a temporary enum with all old and new values
    op.execute("""
        CREATE TYPE workload_action_type_enum_temp AS ENUM (
            'bind', 'create', 'delete', 'move', 'swap_x', 'swap_y',
            'Bind', 'Create', 'Delete', 'Move', 'Swap'
        );
    """)
    # 3. Alter the column to use the temporary enum
    op.execute("""
        ALTER TABLE workload_action
        ALTER COLUMN action_type TYPE workload_action_type_enum_temp
        USING action_type::text::workload_action_type_enum_temp;
    """)
    # 4. Update DB values from old to new using CASE
    op.execute("""
        UPDATE workload_action
        SET action_type = (CASE
            WHEN LOWER(action_type::text) IN ('bind', 'create', 'delete', 'move') THEN LOWER(action_type::text)
            WHEN LOWER(action_type::text) IN ('swap', 'swap_x', 'swap_y') THEN 'swap_x'
            ELSE action_type::text
        END)::workload_action_type_enum_temp
        WHERE action_type IS NOT NULL;
    """)
    # 5. Create the final enum with only new values
    op.execute("""
        CREATE TYPE workload_action_type_enum AS ENUM (
            'bind', 'create', 'delete', 'move', 'swap_x', 'swap_y'
        );
    """)
    # 6. Alter the column to use the final enum
    op.execute("""
        ALTER TABLE workload_action
        ALTER COLUMN action_type TYPE workload_action_type_enum
        USING action_type::text::workload_action_type_enum;
    """)
    # 7. Drop the old and temp enums
    op.execute("DROP TYPE workload_action_type_enum_old;")
    op.execute("DROP TYPE workload_action_type_enum_temp;")
    #------------------------------------------------------------------------

    #------------------------------------------------------------------
    # Upgrade pod_parent_type_enum in a safe way (like workload_action_type_enum)
    # 1. Rename the current enum
    op.execute("""
        ALTER TYPE pod_parent_type_enum RENAME TO pod_parent_type_enum_old;
    """)
    # 2. Create a temporary enum with all old and new values (lowercase)
    op.execute("""
        CREATE TYPE pod_parent_type_enum_temp AS ENUM (
            'deployment', 'statefulset', 'replicaset', 'job', 'daemonset', 'cronjob', 
            'Deployment', 'StatefulSet', 'ReplicaSet', 'Job', 'DaemonSet', 'CronJob'
        );
    """)
    # 3. Alter the column to use the temporary enum
    op.execute("""
        ALTER TABLE workload_action
        ALTER COLUMN pod_parent_type TYPE pod_parent_type_enum_temp
        USING LOWER(pod_parent_type::text)::pod_parent_type_enum_temp;
    """)
    op.execute("""
        ALTER TABLE workload_request_decision
        ALTER COLUMN pod_parent_kind TYPE pod_parent_type_enum_temp
        USING LOWER(pod_parent_kind::text)::pod_parent_type_enum_temp;
    """)
    # 4. Create the final enum with only new values (lowercase)
    op.execute("""
        CREATE TYPE pod_parent_type_enum AS ENUM (
            'deployment', 'statefulset', 'replicaset', 'job', 'daemonset', 'cronjob'
        );
    """)
    # 5. Alter the columns to use the final enum
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
    # 6. Drop the old and temp enums
    op.execute("DROP TYPE pod_parent_type_enum_old;")
    op.execute("DROP TYPE pod_parent_type_enum_temp;")
    #------------------------------------------------------------------

    #------------------------------------------------------------------
    # Upgrade workload_action_status_enum in a safe way (like workload_action_type_enum)
    # 1. Rename action_status_enum to workload_action_status_enum
    op.execute("ALTER TYPE action_status_enum RENAME TO workload_action_status_enum;")
    # 2. Rename the old enum type
    op.execute("ALTER TYPE workload_action_status_enum RENAME TO workload_action_status_enum_old;")
    # 3. Create a temporary enum with all old and new values
    op.execute("""
        CREATE TYPE workload_action_status_enum_temp AS ENUM (
            'pending', 'successful', 'failed', 'partial', 'succeeded'
        );
    """)
    # 4. Alter the column to use the temporary enum
    op.execute("""
        ALTER TABLE workload_action
        ALTER COLUMN action_status TYPE workload_action_status_enum_temp
        USING action_status::text::workload_action_status_enum_temp;
    """)
    # 5. Update DB values if needed (e.g., 'successful' -> 'succeeded' if you want to normalize)
    # (Skip if no normalization needed, otherwise add an UPDATE statement here)
    op.execute("""
        UPDATE workload_action
        SET action_status = CASE
            WHEN action_status = 'successful' THEN 'succeeded'
            WHEN action_status = 'partial' THEN 'pending'
            ELSE action_status
        END
        WHERE action_status IN ('successful', 'partial');
    """)
    # 6. Create the final enum with only new values
    op.execute("""
        CREATE TYPE workload_action_status_enum AS ENUM (
            'pending', 'succeeded', 'failed'
        );
    """)
    # 7. Alter the column to use the final enum
    op.execute("""
        ALTER TABLE workload_action
        ALTER COLUMN action_status TYPE workload_action_status_enum
        USING action_status::text::workload_action_status_enum;
    """)
    # 8. Drop the old and temp enums
    op.execute("DROP TYPE workload_action_status_enum_old;")
    op.execute("DROP TYPE workload_action_status_enum_temp;")
    #------------------------------------------------------------------


def downgrade() -> None:
    """Downgrade schema by restoring old enum values and types."""

    # 1. Rename the current enum to temp
    op.execute("""
        ALTER TYPE workload_action_type_enum RENAME TO workload_action_type_enum_temp;
    """)
    # 2. Create the old enum with all old and new values
    op.execute("""
        CREATE TYPE workload_action_type_enum_old AS ENUM (
            'bind', 'create', 'delete', 'move', 'swap_x', 'swap_y',
            'Bind', 'Create', 'Delete', 'Move', 'Swap'
        );
    """)
    # 3. Alter the column to use the old enum
    op.execute("""
        ALTER TABLE workload_action
        ALTER COLUMN action_type TYPE workload_action_type_enum_old
        USING action_type::text::workload_action_type_enum_old;
    """)
    # 4. Update DB values from new to old using CASE
    op.execute("""
        UPDATE workload_action
        SET action_type = (
            CASE
                WHEN action_type IN ('bind', 'create', 'delete', 'move') THEN INITCAP(action_type::text)
                WHEN action_type IN ('swap_x', 'swap_y') THEN 'Swap'
                ELSE action_type::text
            END
        )::workload_action_type_enum_old
        WHERE action_type IS NOT NULL;
    """)
    # 5. Create the final enum with only old values
    op.execute("""
        CREATE TYPE workload_action_type_enum AS ENUM (
            'Bind', 'Create', 'Delete', 'Move', 'Swap'
        );
    """)
    # 6. Alter the column to use the final enum
    op.execute("""
        ALTER TABLE workload_action
        ALTER COLUMN action_type TYPE workload_action_type_enum
        USING action_type::text::workload_action_type_enum;
    """)
    # 7. Drop the temp and old enums
    op.execute("DROP TYPE workload_action_type_enum_temp;")
    op.execute("DROP TYPE workload_action_type_enum_old;")
    #-------------------------------------------------------------

    #-------------------------------------------------------------
    # Downgrade pod_parent_type_enum in a safe way (like upgrade)
    # 1. Rename the current enum to temp
    op.execute("""
        ALTER TYPE pod_parent_type_enum RENAME TO pod_parent_type_enum_temp;
    """)
    # 2. Create the old enum with all old and new values (camel case and lowercase)
    op.execute("""
        CREATE TYPE pod_parent_type_enum_old AS ENUM (
            'deployment', 'statefulset', 'replicaset', 'job', 'daemonset', 'cronjob',
            'Deployment', 'StatefulSet', 'ReplicaSet', 'Job', 'DaemonSet', 'CronJob'
        );
    """)
    # 3. Alter the columns to use the old enum
    op.execute("""
        ALTER TABLE workload_action
        ALTER COLUMN pod_parent_type TYPE pod_parent_type_enum_old
        USING pod_parent_type::text::pod_parent_type_enum_old;
    """)
    op.execute("""
        ALTER TABLE workload_request_decision
        ALTER COLUMN pod_parent_kind TYPE pod_parent_type_enum_old
        USING pod_parent_kind::text::pod_parent_type_enum_old;
    """)
    # 4. Update DB values from lowercase to camel case
    op.execute("""
        UPDATE workload_action
        SET pod_parent_type = CASE
            WHEN pod_parent_type IN ('deployment') THEN 'Deployment'
            WHEN pod_parent_type IN ('statefulset') THEN 'StatefulSet'
            WHEN pod_parent_type IN ('replicaset') THEN 'ReplicaSet'
            WHEN pod_parent_type IN ('job') THEN 'Job'
            WHEN pod_parent_type IN ('daemonset') THEN 'DaemonSet'
            WHEN pod_parent_type IN ('cronjob') THEN 'CronJob'
            ELSE pod_parent_type
        END
        WHERE pod_parent_type IS NOT NULL;
    """)
    op.execute("""
        UPDATE workload_request_decision
        SET pod_parent_kind = CASE
            WHEN pod_parent_kind IN ('deployment') THEN 'Deployment'
            WHEN pod_parent_kind IN ('statefulset') THEN 'StatefulSet'
            WHEN pod_parent_kind IN ('replicaset') THEN 'ReplicaSet'
            WHEN pod_parent_kind IN ('job') THEN 'Job'
            WHEN pod_parent_kind IN ('daemonset') THEN 'DaemonSet'
            WHEN pod_parent_kind IN ('cronjob') THEN 'CronJob'
            ELSE pod_parent_kind
        END
        WHERE pod_parent_kind IS NOT NULL;
    """)
    # 5. Create the final enum with only camel case values
    op.execute("""
        CREATE TYPE pod_parent_type_enum AS ENUM (
            'Deployment', 'StatefulSet', 'ReplicaSet', 'Job', 'DaemonSet', 'CronJob'
        );
    """)
    # 6. Alter the columns to use the final enum
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
    # 7. Drop the temp and old enums
    op.execute("DROP TYPE pod_parent_type_enum_temp;")
    op.execute("DROP TYPE pod_parent_type_enum_old;")
    #-------------------------------------------------------------

    # #---------------------------------------------------------
    # Downgrade workload_action_status_enum to its original state
    # 1. Rename the current enum to temp
    op.execute("""
        ALTER TYPE workload_action_status_enum RENAME TO workload_action_status_enum_temp;
    """)
    # 2. Create the old enum with original values
    op.execute("""
        CREATE TYPE workload_action_status_enum_old AS ENUM (
            'pending', 'successful', 'failed', 'partial', 'succeeded'
        );
    """)
    # 3. Alter the column to use the old enum
    op.execute("""
        ALTER TABLE workload_action
        ALTER COLUMN action_status TYPE workload_action_status_enum_old
        USING action_status::text::workload_action_status_enum_old;
    """)
    # 4. Restore old values in the table
    op.execute("""
        UPDATE workload_action
        SET action_status = CASE
            WHEN action_status = 'succeeded' THEN 'successful'
            ELSE action_status
        END
        WHERE action_status IN ('succeeded', 'pending');
    """)
    # 5. Create the original enum type
    op.execute("""
        CREATE TYPE workload_action_status_enum AS ENUM (
            'pending', 'successful', 'failed', 'partial'
        );
    """)
    # 6. Alter the column to use the original enum
    op.execute("""
        ALTER TABLE workload_action
        ALTER COLUMN action_status TYPE workload_action_status_enum
        USING action_status::text::workload_action_status_enum;
    """)
    # 7. Drop the temp and old enums
    op.execute("DROP TYPE workload_action_status_enum_temp;")
    op.execute("DROP TYPE workload_action_status_enum_old;")
    # 5. Rename the workload_action_status_enum back to action_status_enum
    op.execute("ALTER TYPE workload_action_status_enum RENAME TO action_status_enum;")
    #-------------------------------------------------------------
