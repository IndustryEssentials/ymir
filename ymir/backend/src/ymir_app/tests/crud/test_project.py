from typing import Any
from random import randint

from sqlalchemy.orm import Session

from app import crud, schemas
from tests.utils.projects import create_project_record
from tests.utils.utils import random_lower_string


def test_get_all_projects(db: Session, mocker: Any) -> None:
    user_id = randint(100, 200)
    project = create_project_record(db, user_id)
    projects = crud.project.get_all_projects(db, limit=100)
    assert project.id in [p.id for p in projects]


def test_create_project(db: Session, mocker: Any) -> None:
    user_id = randint(100, 200)
    j = {"name": random_lower_string(), "training_keywords": [random_lower_string() for _ in range(3)]}
    in_ = schemas.ProjectCreate(**j)
    record = crud.project.create_project(db, obj_in=in_, user_id=user_id)
    fetched_record = crud.project.get(db, id=record.id)
    assert record.name == fetched_record.name


def test_get_multiple_projects(db: Session, mocker: Any) -> None:
    user_id = randint(1000, 2000)
    for i in range(3):
        create_project_record(db, user_id, name=f"prefix_{i}")
    _, count = crud.project.get_multi_projects(db, user_id=user_id, name="prefix_")
    assert count == 3
