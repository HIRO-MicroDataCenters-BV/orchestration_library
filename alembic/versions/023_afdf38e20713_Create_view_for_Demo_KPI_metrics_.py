"""Create view for Demo KPI metrics

Revision ID: afdf38e20713
Revises: 08e8a554b2e9
Create Date: 2025-12-09 15:57:15.254545

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'afdf38e20713'
down_revision: Union[str, None] = '08e8a554b2e9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
        CREATE OR REPLACE VIEW public.kpi_metrics_demo AS
        SELECT
            kpi.request_decision_id,
            kpi.gm_cpu_utilization,
            kpi.gm_mem_utilization,
            kpi.gm_decision_time_in_seconds,
            wrd.pod_name,
            wrd.is_elastic,
            wrd.decision_start_time
        FROM public.kpi_metrics_geometric_mean AS kpi
        JOIN public.workload_request_decision AS wrd
            ON kpi.request_decision_id = wrd.id
        ORDER BY wrd.decision_start_time DESC;
        """
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP VIEW IF EXISTS public.kpi_metrics_demo;")
    # ### end Alembic commands ###
