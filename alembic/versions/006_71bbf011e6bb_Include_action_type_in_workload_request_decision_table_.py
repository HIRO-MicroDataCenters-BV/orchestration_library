"""Include action_type in workload_request_decision table

Revision ID: 71bbf011e6bb
Revises: 2f4fda3d071b
Create Date: 2025-08-06 21:24:34.380604

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "71bbf011e6bb"
down_revision: Union[str, None] = "2f4fda3d071b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Rename the current enum type
    op.execute("ALTER TYPE workload_request_decision_status_enum RENAME TO workload_request_decision_status_enum_old;")

    # 2. Create a temporary enum with all old and new values
    op.execute("""
        CREATE TYPE workload_request_decision_status_enum_temp AS ENUM (
            'pending', 'successful', 'failed', 'succeeded'
        );
    """)

    # 3. Alter the column to use the temporary enum
    op.execute("""
        ALTER TABLE workload_request_decision
        ALTER COLUMN decision_status TYPE workload_request_decision_status_enum_temp
        USING decision_status::text::workload_request_decision_status_enum_temp;
    """)

    # 4. Update all existing rows from 'successful' to 'succeeded'
    op.execute("""
        UPDATE workload_request_decision
        SET decision_status = 'succeeded'
        WHERE decision_status = 'successful';
    """)

    # 5. Create the final enum with only the new values
    op.execute("""
        CREATE TYPE workload_request_decision_status_enum AS ENUM (
            'pending', 'succeeded', 'failed'
        );
    """)

    # 6. Alter the column to use the final enum
    op.execute("""
        ALTER TABLE workload_request_decision
        ALTER COLUMN decision_status TYPE workload_request_decision_status_enum
        USING decision_status::text::workload_request_decision_status_enum;
    """)

    # 7. Drop the old and temp enums
    op.execute("DROP TYPE workload_request_decision_status_enum_old;")
    op.execute("DROP TYPE workload_request_decision_status_enum_temp;")


    op.add_column(
        "workload_request_decision",
        sa.Column(
            "action_type",
            sa.Enum(
                "bind",
                "create",
                "delete",
                "move",
                "swap_x",
                "swap_y",
                name="workload_action_type_enum",
            ),
            nullable=True,
        ),
    )
    op.execute(
        "UPDATE workload_request_decision SET action_type = 'create' WHERE action_type IS NULL"
    )
    op.alter_column("workload_request_decision", "action_type", nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # 1. Rename the current enum type to temp
    op.execute("ALTER TYPE workload_request_decision_status_enum RENAME TO workload_request_decision_status_enum_temp;")

    # 2. Create the old enum with original values
    op.execute("""
        CREATE TYPE workload_request_decision_status_enum_old AS ENUM (
            'pending', 'successful', 'failed', 'succeeded'
        );
    """)

    # 3. Alter the column to use the old enum
    op.execute("""
        ALTER TABLE workload_request_decision
        ALTER COLUMN decision_status TYPE workload_request_decision_status_enum_old
        USING decision_status::text::workload_request_decision_status_enum_old;
    """)

    # 4. Restore old values in the table
    op.execute("""
        UPDATE workload_request_decision
        SET decision_status = 'successful'
        WHERE decision_status = 'succeeded';
    """)

    # 5. Create the original enum type
    op.execute("""
        CREATE TYPE workload_request_decision_status_enum AS ENUM (
            'pending', 'successful', 'failed'
        );
    """)

    # 6. Alter the column to use the original enum
    op.execute("""
        ALTER TABLE workload_request_decision
        ALTER COLUMN decision_status TYPE workload_request_decision_status_enum
        USING decision_status::text::workload_request_decision_status_enum;
    """)

    # 7. Drop the temp and old enums
    op.execute("DROP TYPE workload_request_decision_status_enum_temp;")
    op.execute("DROP TYPE workload_request_decision_status_enum_old;")

    op.drop_column("workload_request_decision", "action_type")
    # ### end Alembic commands ###
