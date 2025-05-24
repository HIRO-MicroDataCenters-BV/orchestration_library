"""Alembic environment configuration."""
import os
import asyncio
from logging.config import fileConfig

from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context

# Adjust the import path if your app folder is named 'app'
from app.db.database import Base

# Import all your models here to ensure they are registered with Alembic
from app.models import (
    node, pod, workload_request_decision,
    workload_request, tuning_parameter
)

# The alembic.context module does have a config attribute at runtime,
# but it’s not declared in its type stubs, so static analysis tools complain.
# This is a workaround to avoid to disable the pylint warning.
config = context.config # pylint: disable=no-member
# Use environment variable
db_url = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/orchestration_db",
)
config.set_main_option("sqlalchemy.url", db_url)


fileConfig(config.config_file_name)
target_metadata = Base.metadata


print("Running migrations online...")
print("Models node:", node.__name__)
print("Models pod:", pod.__name__)
print("Models workload_request_decision:", workload_request_decision.__name__)
print("Models workload_request:", workload_request.__name__)
print("Models tuning_parameter:", tuning_parameter.__name__)
print("Database URL:", db_url)

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    context.configure( # pylint: disable=no-member
        url=db_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction(): # pylint: disable=no-member
        context.run_migrations() # pylint: disable=no-member

def do_run_migrations(connection):
    """Run migrations in 'online' mode."""
    context.configure( # pylint: disable=no-member
        connection=connection,
        target_metadata=target_metadata,
    )
    with context.begin_transaction(): # pylint: disable=no-member
        context.run_migrations() # pylint: disable=no-member

async def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = create_async_engine(db_url, future=True)

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()

if context.is_offline_mode(): # pylint: disable=no-member
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
