"""added new columns to alerts table

Revision ID: 586945147dca
Revises: 56c6519f404b
Create Date: 2025-07-18 18:22:36.465423

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '586945147dca'
down_revision: Union[str, None] = '56c6519f404b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('alerts', sa.Column('source_ip', sa.Text(), nullable=True))
    op.add_column('alerts', sa.Column('source_port', sa.Integer(), nullable=True))
    op.add_column('alerts', sa.Column('destination_ip', sa.Text(), nullable=True))
    op.add_column('alerts', sa.Column('destination_port', sa.Integer(), nullable=True))
    op.add_column('alerts', sa.Column('protocol', sa.Text(), nullable=True))
    op.alter_column('alerts', 'alert_model',
               existing_type=sa.TEXT(),
               nullable=False)
    op.alter_column('alerts', 'pod_id',
               existing_type=sa.UUID(),
               nullable=True)
    op.alter_column('alerts', 'node_id',
               existing_type=sa.UUID(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('alerts', 'node_id',
               existing_type=sa.UUID(),
               nullable=False)
    op.alter_column('alerts', 'pod_id',
               existing_type=sa.UUID(),
               nullable=False)
    op.alter_column('alerts', 'alert_model',
               existing_type=sa.TEXT(),
               nullable=True)
    op.drop_column('alerts', 'protocol')
    op.drop_column('alerts', 'destination_port')
    op.drop_column('alerts', 'destination_ip')
    op.drop_column('alerts', 'source_port')
    op.drop_column('alerts', 'source_ip')
    # ### end Alembic commands ###
