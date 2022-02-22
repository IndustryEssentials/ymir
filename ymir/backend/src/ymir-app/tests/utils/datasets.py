from random import randint
from typing import Optional

from sqlalchemy.orm import Session

from app import crud, schemas
from app.constants.state import ResultState
from tests.utils.utils import random_lower_string


def create_dataset_record(
    db: Session,
    user_id: Optional[int] = None,
    project_id: Optional[int] = None,
    dataset_group_id: Optional[int] = None,
    task_id: Optional[int] = None,
    state_: ResultState = ResultState.ready,
):
    j = {
        "name": random_lower_string(),
        "hash": random_lower_string(),
        "result_state": state_,
        "version_num": randint(1, 100),
        "user_id": user_id or randint(100, 200),
        "project_id": project_id or randint(201, 300),
        "dataset_group_id": dataset_group_id or randint(301, 400),
        "task_id": task_id or randint(401, 500),
    }
    in_ = schemas.DatasetCreate(**j)
    record = crud.dataset.create(db, obj_in=in_)
    return record
