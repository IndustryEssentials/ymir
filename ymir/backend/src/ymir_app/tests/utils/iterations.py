from random import randint
from typing import Optional, Dict

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import crud, schemas
from app.config import settings
from tests.utils.projects import create_project_record
from tests.utils.utils import random_lower_string


def create_iteration_record(
    db: Session,
    user_id: Optional[int] = None,
    project_id: Optional[int] = None,
    iteration_round: Optional[int] = None,
    previous_iteration: Optional[int] = None,
    mining_dataset_id: Optional[int] = None,
):
    j = {
        "project_id": project_id or randint(1000, 2000),
        "iteration_round": iteration_round or 1,
        "previous_iteration": previous_iteration or 0,
    }
    if mining_dataset_id:
        j["mining_dataset_id"] = mining_dataset_id
    in_ = schemas.IterationCreate(**j)
    record = crud.iteration.create_with_user_id(db, obj_in=in_, user_id=user_id)
    return record


def create_step_record(
    db: Session,
    user_id: Optional[int] = None,
    project_id: Optional[int] = None,
    iteration_round: Optional[int] = None,
    previous_iteration: Optional[int] = None,
    mining_dataset_id: Optional[int] = None,
):
    j = {
        "project_id": project_id or randint(1000, 2000),
        "previous_iteration": previous_iteration or 0,
    }
    if mining_dataset_id:
        j["mining_dataset_id"] = mining_dataset_id
    in_ = schemas.IterationCreate(**j)
    record = crud.iteration.create_with_user_id(db, obj_in=in_, user_id=user_id)
    return record


def create_iteration_via_api(db: Session, client: TestClient, user_id: int, normal_user_token_headers: Dict) -> Dict:
    project = create_project_record(db, user_id, random_lower_string(), ["person", "cat"])
    payload = {"iteration_round": 1, "previous_iteration": 0, "project_id": project.id}
    r = client.post(f"{settings.API_V1_STR}/iterations/", headers=normal_user_token_headers, json=payload)
    iteration = r.json()["result"]
    return iteration
