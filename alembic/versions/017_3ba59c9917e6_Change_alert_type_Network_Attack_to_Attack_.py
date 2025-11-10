"""Change alert type Network_Attack to Attack

Revision ID: 3ba59c9917e6
Revises: 95259fc5e114
Create Date: 2025-11-07 09:50:11.286446

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3ba59c9917e6'
down_revision: Union[str, None] = '95259fc5e114'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("UPDATE alerts SET alert_type = 'Attack' WHERE alert_type = 'Network-Attack'")
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("UPDATE alerts SET alert_type = 'Network-Attack' WHERE alert_type = 'Attack'")
    # ### end Alembic commands ###
