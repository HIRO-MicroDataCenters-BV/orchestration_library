"""Alembic environment configuration."""
import os
import asyncio
from logging.config import fileConfig

from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context

# Adjust the import path if your app folder is named 'app'
from app.db.database import Base

# Import all your models here to ensure they are registered with Alembic
from app.models import *

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

exclude_tables_list = []


print("Running migrations online...")
print("Database URL:", db_url)

def process_revision_directives(context, revision, directives):
    """Skip generating a revision file when autogenerate finds no changes."""
    if getattr(config, "cmd_opts", None) and getattr(config.cmd_opts, "autogenerate", False):
        if not directives:
            return
        script = directives[0]
        if script.upgrade_ops.is_empty():
            if os.getenv("ALEMBIC_ALLOW_EMPTY") == "1":
                print("No schema changes detected; creating empty revision because ALEMBIC_ALLOW_EMPTY=1.")
                return
            print("No schema changes detected; skipping empty revision.")
            directives[:] = []  # prevents file creation

def include_object(object_, name, type_, reflection, compare_to):
    # Skip view models (flagged with info.is_view) or explicit name
    # print(f"include_object called with name={name}, type_={type_}, "
    #       f"reflection={reflection}, compare_to={compare_to}")
    if type_ == "table":
        if getattr(object_, "info", {}).get("is_view"):
            return False
        if exclude_tables_list and name in exclude_tables_list:
            return False
    return True

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    context.configure( # pylint: disable=no-member
        url=db_url,
        target_metadata=target_metadata,
        include_object=include_object,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        process_revision_directives=process_revision_directives,
    )
    with context.begin_transaction(): # pylint: disable=no-member
        context.run_migrations() # pylint: disable=no-member

def do_run_migrations(connection):
    """Run migrations in 'online' mode."""
    context.configure( # pylint: disable=no-member
        connection=connection,
        target_metadata=target_metadata,
        include_object=include_object,
        process_revision_directives=process_revision_directives,
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
