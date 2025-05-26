"""initiating alembic

Revision ID: cae99e0d2958
Revises: 
Create Date: 2025-05-24 02:02:04.082613

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'cae99e0d2958'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')

    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_tables WHERE tablename = 'workload_request') THEN
            CREATE TABLE workload_request (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                name VARCHAR(255) NOT NULL,
                namespace VARCHAR(255) NOT NULL,
                api_version VARCHAR(50) NOT NULL,
                kind VARCHAR(50) NOT NULL,
                current_scale INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        END IF;
    END $$;
    """)

    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_tables WHERE tablename = 'node') THEN
            CREATE TABLE node (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                name VARCHAR(255) NOT NULL,
                status VARCHAR(50) DEFAULT 'active',
                cpu_capacity FLOAT NOT NULL,
                memory_capacity FLOAT NOT NULL,
                current_cpu_assignment FLOAT,
                current_memory_assignment FLOAT,
                current_cpu_utilization FLOAT,
                current_memory_utilization FLOAT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        END IF;
    END $$;
    """)

    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_tables WHERE tablename = 'pod') THEN
            CREATE TABLE pod (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                name VARCHAR(255),
                namespace VARCHAR(255),
                demand_cpu FLOAT NOT NULL,
                demand_memory FLOAT NOT NULL,
                demand_slack_cpu FLOAT,
                demand_slack_memory FLOAT,
                is_elastic BOOLEAN NOT NULL,
                assigned_node_id UUID,
                workload_request_id UUID NOT NULL,
                status VARCHAR(50) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (assigned_node_id) REFERENCES node(id),
                FOREIGN KEY (workload_request_id) REFERENCES workload_request(id)
            );
        END IF;
    END $$;
    """)

    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_tables WHERE tablename = 'workload_request_decision') THEN
            CREATE TABLE workload_request_decision (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                workload_request_id UUID NOT NULL,
                node_name VARCHAR(255) NOT NULL,
                queue_name VARCHAR(255) NOT NULL,
                status VARCHAR(50) DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (workload_request_id) REFERENCES workload_request(id)
            );
        END IF;
    END $$;
    """)

    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_tables WHERE tablename = 'tuning_parameters') THEN
            CREATE TABLE tuning_parameters (
                id SERIAL PRIMARY KEY,
                output_1 FLOAT,
                output_2 FLOAT,
                output_3 FLOAT,
                alpha FLOAT,
                beta FLOAT,
                gamma FLOAT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        END IF;
    END $$;
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS tuning_parameters;")
    op.execute("DROP TABLE IF EXISTS workload_request_decision;")
    op.execute("DROP TABLE IF EXISTS pod;")
    op.execute("DROP TABLE IF EXISTS node;")
    op.execute("DROP TABLE IF EXISTS workload_request;")