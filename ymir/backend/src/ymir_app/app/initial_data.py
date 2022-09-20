import sys
import logging
from typing import Optional

from alembic.config import Config
from alembic.script import ScriptDirectory
from alembic.util import CommandError

from app.db.init_db import init_db, migrate_data
from app.db.session import SessionLocal
from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init() -> None:
    db = SessionLocal()
    init_db(db)


def should_migrate_data(base_alembic_revision: Optional[str]) -> bool:
    if not base_alembic_revision:
        return False
    base_alembic_revision = base_alembic_revision.split()[0]
    script_dir = ScriptDirectory.from_config(Config("alembic.ini"))
    try:
        revisions = list(script_dir.walk_revisions(base_alembic_revision, settings.MIGRATION_CHECKPOINT))
    except CommandError:
        # base alembic revision already newer than MIGRATION_CHECKPOINT
        return False
    # at least two migration revisions indicate that
    # we do migrate from previous version to MIGRATION_CHECKPOINT
    return len(revisions) > 1


def migrate() -> None:
    db = SessionLocal()
    migrate_data(db)


def main(base_alembic_revision: Optional[str]) -> None:
    logger.info("Creating initial data")
    init()
    logger.info("Initial data created")

    if should_migrate_data(base_alembic_revision):
        logger.info("Data Migration started")
        migrate()
        logger.info("Data migration finished")
    else:
        logger.info("Data migration skipped")


if __name__ == "__main__":
    try:
        base_alembic_revision: Optional[str] = sys.argv[1]
    except IndexError:
        base_alembic_revision = None
    main(base_alembic_revision)
