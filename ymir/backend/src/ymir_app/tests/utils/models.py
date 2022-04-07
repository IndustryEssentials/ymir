from random import randint

from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.constants.state import TaskType
from tests.utils.utils import random_lower_string


def create_model_group_record(
    db: Session,
    user_id: int,
    project_id: int,
):
    j = {
        "name": random_lower_string(),
        "user_id": user_id,
        "project_id": project_id,
    }
    in_ = schemas.ModelGroupCreate(**j)
    record = crud.model_group.create_with_user_id(db, obj_in=in_, user_id=user_id)
    return record


def create_model(db: Session, user_id: int) -> models.Model:
    project_id = randint(100, 200)
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
