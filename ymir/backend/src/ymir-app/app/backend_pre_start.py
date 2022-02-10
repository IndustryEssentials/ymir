import logging

from app.config import settings
from app.db.session import SessionLocal
from app.utils.err import retry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init() -> None:
    db = SessionLocal()
    # Try to create session to check if DB is awake
    db.execute("SELECT 1")


def main() -> None:
    logger.info("Initializing service")
    retry(init, n_times=5, wait=settings.RETRY_INTERVAL_SECONDS)
    logger.info("Service finished initializing")


if __name__ == "__main__":
    main()
