from __future__ import with_statement

from contextlib import contextmanager
import os
import time
import logging
from logging.config import fileConfig
import uuid
import subprocess
from typing import Dict, Optional, Generator

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.db.base import Base  # noqa


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

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


def get_mysql_credentials() -> Dict:
    credentials = {
        "MYSQL_USER": os.getenv("MYSQL_INITIAL_USER"),
        "MYSQL_PASSWORD": os.getenv("MYSQL_INITIAL_PASSWORD"),
        "MYSQL_DATABASE": os.getenv("MYSQL_DATABASE"),
        "MYSQL_HOST": "db",
    }
    if None in credentials.values():
        raise ValueError("Invalid MySQL Environments")
    return credentials


def create_backup(backup_filename: str) -> None:
    credentials = get_mysql_credentials()
    mysqldump_command = (
        "mysqldump --host {MYSQL_HOST} -u {MYSQL_USER} -p{MYSQL_PASSWORD} --databases {MYSQL_DATABASE} --no-tablespaces --ignore-table {MYSQL_DATABASE}.alembic_version --result-file %s"
    ).format(**credentials)
    subprocess.run(mysqldump_command % backup_filename, shell=True, check=True)


def recover_from_backup(backup_filename: str) -> None:
    credentials = get_mysql_credentials()
    recover_command = "mysql --host {MYSQL_HOST} -u {MYSQL_USER} -p{MYSQL_PASSWORD} < %s".format(**credentials)
    subprocess.run(recover_command % backup_filename, shell=True, check=True)


@contextmanager
def backup_database() -> Generator[None, None, None]:
    current_alembic_version = get_current_alembic_version()
    backup_filename: Optional[str] = None
    if is_alembic_migration_command() and current_alembic_version:
        # Only when alembic is upgrading or downgrading
        # and legacy database exists, should we backup database
        backup_filename = f"backup_{current_alembic_version}_{int(time.time())}_{uuid.uuid4().hex}.sql"
        create_backup(backup_filename)
        logging.info("Created MySQL backup to %s" % backup_filename)
    try:
        yield
    except Exception as e:
        if backup_filename:
            recover_from_backup(backup_filename)
            logging.info("Failed to upgrade database (%s), rollback with backup %s" % (e, backup_filename))


def is_alembic_migration_command() -> bool:
    command = context.config.cmd_opts.cmd[0].__name__
    return command in ["upgrade", "downgrade"]


def get_current_alembic_version() -> Optional[str]:
    migration_context = context.get_context()
    return migration_context.get_current_revision()


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

        with backup_database():
            with context.begin_transaction():
                context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
