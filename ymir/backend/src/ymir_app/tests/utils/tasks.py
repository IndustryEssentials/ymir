from random import randint
from typing import Optional

from sqlalchemy.orm import Session

from app import crud, schemas
from app.constants.state import TaskType, TaskState
from tests.utils.utils import random_lower_string
from tests.utils.datasets import create_dataset_record


def create_task(
    db: Session,
    user_id: int,
    project_id: Optional[int] = None,
    type_: TaskType = TaskType.mining,
    state: TaskState = TaskState.done,
):
    project_id = project_id or randint(100, 200)
    j = {
        "name": random_lower_string(),
        "type": type_,
        "project_id": project_id,
        "parameters": {"dataset_id": randint(100, 200)},
        "state": state,
    }
    task_in = schemas.TaskCreate(**j)
    task = crud.task.create_task(db, obj_in=task_in, task_hash=random_lower_string(), user_id=user_id)
    create_dataset_record(db, user_id, project_id, task_id=task.id)
    return task
