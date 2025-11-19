"""fix gm_decision_time_in_seconds in kpi_metrics_geometric_mean view

Revision ID: 11d18c468b34
Revises: 6a83507194b9
Create Date: 2025-11-19 12:22:04.203074

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '11d18c468b34'
down_revision: Union[str, None] = '6a83507194b9'
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
        COALESCE(
            EXP(AVG(LN(NULLIF(decision_time_in_seconds, 0)))),
            0
        ) AS gm_decision_time_in_seconds,
        MAX(created_at) AS last_created_at,
        MAX(id) AS last_seq_id
    FROM kpi_metrics
    WHERE cpu_utilization > 0 AND mem_utilization > 0
    GROUP BY request_decision_id;
    """)


def downgrade() -> None:
    """Downgrade schema."""
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
