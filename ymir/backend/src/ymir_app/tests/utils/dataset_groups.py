from random import randint
from typing import Optional

from sqlalchemy.orm import Session

from app import crud, schemas
from tests.utils.utils import random_lower_string


def create_dataset_group_record(
    db: Session,
    user_id: int,
    project_id: Optional[int] = None,
):
    j = {
        "name": random_lower_string(),
        "project_id": project_id or randint(201, 300),
        "user_id": user_id,
    }
    in_ = schemas.DatasetGroupCreate(**j)
    record = crud.dataset_group.create(db, obj_in=in_)
    return record
