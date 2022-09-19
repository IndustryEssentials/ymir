import logging

from app.db.init_db import init_db, migrate_data
from app.db.session import SessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init() -> None:
    db = SessionLocal()
    init_db(db)


def migrate() -> None:
    # todo
    #  get current version from controller,
    #  only when current version < 1.3.0 should we run migration
    db = SessionLocal()
    migrate_data(db)


def main() -> None:
    logger.info("Creating initial data")
    init()
    logger.info("Initial data created; Data Migration started")
    migrate()
    logger.info("Data migration finished")


if __name__ == "__main__":
    main()
