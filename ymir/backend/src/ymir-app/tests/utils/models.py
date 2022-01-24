from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.config import settings
from app.constants.state import TaskType
from tests.utils.utils import random_lower_string


def create_model(db: Session, client: TestClient, token) -> models.Model:
    r = client.get(f"{settings.API_V1_STR}/users/me", headers=token)
    user_id = r.json()["result"]["id"]
    task_in = schemas.TaskCreate(
        name=random_lower_string(6),
        type=TaskType.training,
    )
    task = crud.task.create(db, obj_in=task_in)
    model_in = schemas.ModelCreate(
        hash=random_lower_string(10),
        name=random_lower_string(6),
        user_id=user_id,
        task_id=task.id,
    )
    model = crud.model.create(db, obj_in=model_in)
    return model
