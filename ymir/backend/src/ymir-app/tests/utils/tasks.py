from random import randint
from sqlalchemy.orm import Session

from typing import Optional

from app import crud, schemas
from app.constants.state import TaskType
from tests.utils.utils import random_lower_string


def create_task(
    db: Session,
    user_id: int,
    project_id: Optional[int] = None,
    type_: TaskType = TaskType.mining,
):
    j = {
        "name": random_lower_string(),
        "type": type_,
        "project_id": project_id or randint(100, 200),
    }
    task_in = schemas.TaskCreate(**j)
    task = crud.task.create_task(
        db, obj_in=task_in, task_hash=random_lower_string(), user_id=user_id
    )
    return task
