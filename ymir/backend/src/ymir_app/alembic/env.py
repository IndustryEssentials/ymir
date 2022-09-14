from __future__ import with_statement

import os
import time
from logging.config import fileConfig
import uuid

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.db.base import Base  # noqa

from .backup_util import create_backup, recover_from_backup

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config
migration_context = context.get_context()
current_alembic_version = context.get_current_revision()

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
# target_metadata = None

target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def get_url() -> str:
    return os.getenv("DATABASE_URI", "sqlite:///app.db")


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            # new feature, for sqlite alter
            render_as_batch=True,
        )

        # todo
        #  specify backup locations in alembic.ini
        backup_filename = f"backup_{current_alembic_version}_{time.time()}_{uuid.uuid4().hex}"
        create_backup(backup_filename)
        with context.begin_transaction():
            try:
                context.run_migrations()
            except Exception as e:
                print("Failed to upgrade database (%s), rollback with backup %s" % (e, backup_filename))
                recover_from_backup(backup_filename)


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
