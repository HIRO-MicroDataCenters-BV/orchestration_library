"""Rename workload decission to workload request decision

Revision ID: 7f3e89894680
Revises: 9f5ab71e4ed1
Create Date: 2025-06-24 11:45:45.196432

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '7f3e89894680'
down_revision: Union[str, None] = '9f5ab71e4ed1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('workload_request_decision',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('pod_id', sa.UUID(), nullable=False),
    sa.Column('pod_name', sa.String(length=255), nullable=False),
    sa.Column('namespace', sa.String(length=255), nullable=False),
    sa.Column('node_id', sa.UUID(), nullable=False),
    sa.Column('is_elastic', sa.Boolean(), nullable=False),
    sa.Column('queue_name', sa.String(length=255), nullable=False),
    sa.Column('demand_cpu', sa.Float(), nullable=False),
    sa.Column('demand_memory', sa.Float(), nullable=False),
    sa.Column('demand_slack_cpu', sa.Float(), nullable=True),
    sa.Column('demand_slack_memory', sa.Float(), nullable=True),
    sa.Column('is_decision_status', sa.Boolean(), nullable=False),
    sa.Column('pod_parent_id', sa.UUID(), nullable=False),
    sa.Column('pod_parent_kind', sa.String(length=100), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('workload_decision')
    op.add_column('workload_action', sa.Column('id', sa.UUID(), nullable=False))
    op.drop_index('ix_workload_action_action_id', table_name='workload_action')
    op.create_index(op.f('ix_workload_action_id'), 'workload_action', ['id'], unique=True)
    op.drop_column('workload_action', 'action_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('workload_action', sa.Column('action_id', sa.UUID(), autoincrement=False, nullable=False))
    op.drop_index(op.f('ix_workload_action_id'), table_name='workload_action')
    op.create_index('ix_workload_action_action_id', 'workload_action', ['action_id'], unique=True)
    op.drop_column('workload_action', 'id')
    op.create_table('workload_decision',
    sa.Column('id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('pod_id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('pod_name', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('namespace', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('node_id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('is_elastic', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.Column('queue_name', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('demand_cpu', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False),
    sa.Column('demand_memory', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False),
    sa.Column('demand_slack_cpu', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
    sa.Column('demand_slack_memory', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
    sa.Column('is_decision_status', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.Column('pod_parent_id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('pod_parent_kind', sa.VARCHAR(length=100), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), autoincrement=False, nullable=True),
    sa.Column('updated_at', postgresql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='workload_decision_pkey')
    )
    op.drop_table('workload_request_decision')
    # ### end Alembic commands ###
