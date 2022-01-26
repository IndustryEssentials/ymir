from sqlalchemy.orm import Session

from app import crud, schemas
from app.constants.state import TaskType
from tests.utils.utils import random_lower_string


def create_task(db: Session, user_id: int, type_: TaskType = TaskType.mining):
    j = {"name": random_lower_string(), "type": type_}
    task_in = schemas.TaskCreate(**j)
    task = crud.task.create_task(
        db, obj_in=task_in, task_hash=random_lower_string(), user_id=user_id
    )
    return task
