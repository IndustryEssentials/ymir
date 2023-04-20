import logging


from app import crud, schemas
from app.config import settings
from app.db.session import SessionLocal
from app.libs.tasks import create_pull_docker_image_task

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_docker_image() -> None:
    db = SessionLocal()
    docker_image_in = schemas.image.DockerImageCreate(
        name=settings.OFFICIAL_DOCKER_IMAGE_NAME,
        url=settings.OFFICIAL_DOCKER_IMAGE_URL,
        is_official=True,
    )
    if crud.docker_image.get_by_url(db, docker_image_in.url) or crud.docker_image.get_by_name(db, docker_image_in.name):
        return

    init_user_id = 1
    create_pull_docker_image_task(db, init_user_id, docker_image_in)


def main() -> None:
    logger.info("Prepare to pull official docker image")
    try:
        init_docker_image()
    except Exception:
        logger.exception("Failed to pull docker image. Please refer to app log")
    else:
        logger.info("Started pulling official docker image")


if __name__ == "__main__":
    main()
