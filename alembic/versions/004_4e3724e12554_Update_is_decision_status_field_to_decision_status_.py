"""Update is_decision_status field to decision_status

Revision ID: 4e3724e12554
Revises: 586945147dca
Create Date: 2025-07-28 14:12:54.614960

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4e3724e12554'
down_revision: Union[str, None] = '586945147dca'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade() -> None:
    """Upgrade schema."""
    # 0. Create the ENUM type first
    decision_status_enum = sa.Enum('pending', 'successful', 'failed', name='workload_request_decision_status_enum')
    decision_status_enum.create(op.get_bind(), checkfirst=True)

    # 1. Add new column as nullable
    op.add_column(
        'workload_request_decision',
        sa.Column(
            'decision_status',
            decision_status_enum,
            nullable=True
        )
    )
    # 2. Data migration
    op.execute(
        """
        UPDATE workload_request_decision
        SET decision_status = 
            (CASE
                WHEN is_decision_status IS TRUE THEN 'successful'
                WHEN is_decision_status IS FALSE THEN 'failed'
                ELSE 'pending'
            END)::workload_request_decision_status_enum
        """
    )
    # 3. Alter to NOT NULL
    op.alter_column('workload_request_decision', 'decision_status', nullable=False)
    # 4. Drop old column
    op.drop_column('workload_request_decision', 'is_decision_status')


def downgrade() -> None:
    """Downgrade schema."""
    # 1. Add old column as nullable
    op.add_column(
        'workload_request_decision',
        sa.Column('is_decision_status', sa.BOOLEAN(), autoincrement=False, nullable=True)
    )
    # 2. Data migration (reverse)
    op.execute(
        """
        UPDATE workload_request_decision
        SET is_decision_status =
            CASE
                WHEN decision_status = 'successful' THEN TRUE
                WHEN decision_status = 'failed' THEN FALSE
                ELSE NULL
            END
        """
    )
    # 3. Alter to NOT NULL
    op.alter_column('workload_request_decision', 'is_decision_status', nullable=False)
    # 4. Drop new column
    op.drop_column('workload_request_decision', 'decision_status')
    # 5. Drop the ENUM type
    decision_status_enum = sa.Enum('pending', 'successful', 'failed', name='workload_request_decision_status_enum')
    decision_status_enum.drop(op.get_bind(), checkfirst=True)
