from random import randint
from typing import Optional

from sqlalchemy.orm import Session

from app import crud, schemas
from tests.utils.utils import random_lower_string
from tests.utils.datasets import create_dataset_group_record


def create_project_record(
    db: Session,
    user_id: Optional[int] = None,
    name: Optional[str] = None,
):
    name = name or random_lower_string()
    user_id = user_id or randint(1, 20)
    j = {"name": name, "training_keywords": [random_lower_string() for _ in range(3)]}
    in_ = schemas.ProjectCreate(**j)
    record = crud.project.create_project(db, obj_in=in_, user_id=user_id)

    training_dataset_group = create_dataset_group_record(db, user_id, record.id)
    record = crud.project.update_resources(
        db,
        project_id=record.id,
        project_update=schemas.ProjectUpdate(training_dataset_group_id=training_dataset_group.id),
    )
    return record
