from random import randint

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.constants.state import TaskType
from tests.utils.utils import random_lower_string


def create_model(db: Session, client: TestClient, user_id: int) -> models.Model:
    project_id = randint(100, 200)
    task = crud.task.create_placeholder(db, type_=TaskType.training, user_id=user_id, project_id=project_id)
    model_in = schemas.ModelCreate(
        hash=random_lower_string(10),
        name=random_lower_string(6),
        user_id=user_id,
        task_id=task.id,
        project_id=project_id,
        model_group_id=randint(1000, 2000),
    )
    model = crud.model.create_with_version(db, obj_in=model_in)
    return model
