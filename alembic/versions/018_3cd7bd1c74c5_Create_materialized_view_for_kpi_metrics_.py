"""Create view for kpi metrics

Revision ID: 3cd7bd1c74c5
Revises: 3ba59c9917e6
Create Date: 2025-11-12 12:40:52.658440

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '3cd7bd1c74c5'
down_revision: Union[str, None] = '3ba59c9917e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
    CREATE OR REPLACE VIEW kpi_metrics_geometric_mean AS
    SELECT
        request_decision_id,
        EXP(AVG(LN(cpu_utilization))) AS gm_cpu_utilization,
        EXP(AVG(LN(mem_utilization))) AS gm_mem_utilization,
        EXP(AVG(LN(NULLIF(decision_time_in_seconds, 0)))) AS gm_decision_time_in_seconds,
        MAX(created_at) AS last_created_at,
        MAX(id) AS last_seq_id
    FROM kpi_metrics
    WHERE cpu_utilization > 0 AND mem_utilization > 0
    GROUP BY request_decision_id;
    """)



def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP VIEW IF EXISTS kpi_metrics_geometric_mean;")
