import logging
from typing import List

from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.config import settings
from app.constants.state import TaskState, TaskType
from app.db.session import SessionLocal
from app.models.task import Task
from app.utils.err import catch_error_and_report
from app.utils.ymir_controller import ControllerClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def list_unfinished_tasks(db: Session) -> List[Task]:
    tasks = crud.task.get_tasks_by_states(
        db,
        states=[TaskState.pending, TaskState.running, TaskState.premature],
        including_deleted=True,
    )
    return tasks


def terminate_tasks() -> None:
    db = SessionLocal()
    controller = ControllerClient(settings.GRPC_CHANNEL)
    user = crud.user.get_by_email(db, email=settings.FIRST_ADMIN)
    if not user:
        logger.error("No initial user yet, quit")
        return
    for task in list_unfinished_tasks(db):
        if not (task.hash and task.type):
            # make mypy happy
            continue
        try:
            controller.terminate_task(
                user_id=user.id, task_hash=task.hash, task_type=task.type
            )
        except Exception:
            # terminate legacy tasks shouldn't break start up process
            logger.info("Failed to terminate legacy task: %s", task.hash)
            continue


def main() -> None:
    logger.info("Cleaning legacy tasks upon start up")
    # todo
    #  put the whole terminating process into background
    terminate_tasks()
    logger.info("Cleaned legacy tasks")


if __name__ == "__main__":
    main()
