import logging
from typing import List

from sqlalchemy.orm import Session

from app import crud
from app.config import settings
from app.constants.state import RunningStates, TaskState
from app.db.session import SessionLocal
from app.models.task import Task
from app.utils.ymir_controller import ControllerClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def list_unfinished_tasks(db: Session) -> List[Task]:
    tasks = crud.task.get_tasks_by_states(
        db,
        states=RunningStates,
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
        if task.type in settings.TASK_TYPES_WHITELIST:
            # do not terminate task having whitelist type
            continue
        try:
            controller.terminate_task(user_id=user.id, task_hash=task.hash, task_type=task.type)
        except Exception:
            # terminate legacy tasks shouldn't break start up process
            logger.info("Failed to terminate legacy task: %s", task.hash)
            continue
        else:
            crud.task.update_state(db, task=task, new_state=TaskState.error)
            if task.result_model:  # type: ignore
                crud.model.set_result_state_to_error(db, id=task.result_model.id)  # type: ignore
            if task.result_dataset:  # type: ignore
                crud.dataset.set_result_state_to_error(db, id=task.result_dataset.id)  # type: ignore


def main() -> None:
    logger.info("Cleaning legacy tasks upon start up")
    # todo
    #  put the whole terminating process into background
    terminate_tasks()
    logger.info("Cleaned legacy tasks")


if __name__ == "__main__":
    main()
