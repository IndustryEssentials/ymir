from typing import Optional
from random import randint

from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.constants.state import TaskType
from tests.utils.utils import random_lower_string


def create_model_group_record(
    db: Session,
    user_id: int,
    project_id: Optional[int] = None,
    training_dataset_id: Optional[int] = None,
):
    project_id = project_id or randint(100, 200)
    training_dataset_id = training_dataset_id or randint(1000, 2000)
    j = {
        "name": random_lower_string(),
        "user_id": user_id,
        "project_id": project_id,
        "training_dataset_id": training_dataset_id,
    }
    in_ = schemas.ModelGroupCreate(**j)
    record = crud.model_group.create_with_user_id(db, obj_in=in_, user_id=user_id)
    return record


def create_model(
    db: Session, user_id: int, group_id: Optional[int] = None, project_id: Optional[int] = None
) -> models.Model:
    project_id = project_id or randint(100, 200)
    if not group_id:
        group = create_model_group_record(db, user_id, project_id)
        group_id = group.id

    task = crud.task.create_placeholder(db, type_=TaskType.training, user_id=user_id, project_id=project_id)
    model_in = schemas.ModelCreate(
        hash=random_lower_string(10),
        name=random_lower_string(6),
        user_id=user_id,
        task_id=task.id,
        source=task.type,
        project_id=project_id,
        model_group_id=group_id,
    )
    model = crud.model.create_with_version(db, obj_in=model_in)
    return model
