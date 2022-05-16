import logging
from typing import List, Iterator, Dict
from concurrent.futures import ThreadPoolExecutor
from functools import partial

from sqlalchemy.orm import Session

from app import crud
from app.config import settings
from app.db.session import SessionLocal
from app.models.project import Project
from app.utils.ymir_controller import ControllerClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def iter_all_projects(db: Session, batch_size: int = settings.DEFAULT_LIMIT) -> Iterator[List[Project]]:
    offset = 0
    projects = crud.project.get_all_projects(db, offset=offset, limit=batch_size)
    while projects:
        yield projects
        offset = offset + batch_size
        projects = crud.project.get_all_projects(db, offset=offset, limit=batch_size)


def fix_repo(controller: ControllerClient, project: Project) -> Dict:
    return controller.fix_repo(user_id=project.user_id, project_id=project.id)


def batch_fix_repos(controller: ControllerClient, projects: List[Project]) -> List:
    f_fix_repo = partial(fix_repo, controller)
    with ThreadPoolExecutor() as executor:
        res = executor.map(f_fix_repo, projects)
    return list(res)


def fix_all_repos() -> None:
    db = SessionLocal()
    controller = ControllerClient()
    for project_batch in iter_all_projects(db):
        try:
            batch_fix_repos(controller, project_batch)
        except Exception:
            # fix dirty repos shouldn't break start up process
            logger.exception("Failed to clean a batch of repos: %s", project_batch)


def main() -> None:
    logger.info("Fix all dirty repos upon start up")
    fix_all_repos()
    logger.info("Fixed dirty repos")


if __name__ == "__main__":
    main()
