from random import randint
from typing import Optional

from sqlalchemy.orm import Session

from app import crud, schemas
from app.constants.state import ResultState, TaskType
from tests.utils.utils import random_lower_string


def create_dataset_group_record(
    db: Session,
    user_id: Optional[int] = None,
    project_id: Optional[int] = None,
):
    j = {
        "name": random_lower_string(),
        "user_id": user_id or randint(100, 200),
        "project_id": project_id or randint(201, 300),
    }
    in_ = schemas.DatasetGroupCreate(**j)
    record = crud.dataset_group.create(db, obj_in=in_)
    return record


def create_dataset_record(
    db: Session,
    user_id: Optional[int] = None,
    project_id: Optional[int] = None,
    dataset_group_id: Optional[int] = None,
    task_id: Optional[int] = None,
    state_: ResultState = ResultState.ready,
):
    if not dataset_group_id:
        group = create_dataset_group_record(db, user_id, project_id)
        dataset_group_id = group.id

    j = {
        "hash": random_lower_string(),
        "source": TaskType.training,
        "result_state": state_,
        "user_id": user_id or randint(100, 200),
        "project_id": project_id or randint(201, 300),
        "dataset_group_id": dataset_group_id,
        "task_id": task_id or randint(401, 500),
    }
    in_ = schemas.DatasetCreate(**j)
    record = crud.dataset.create_with_version(db, obj_in=in_)
    return record
