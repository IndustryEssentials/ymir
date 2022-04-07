from random import randint

from sqlalchemy.orm import Session

from app import crud
from app.schemas.model import ModelCreate
from tests.utils.utils import random_hash
from tests.utils.models import create_model_group_record


def test_create_model(db: Session) -> None:
    user_id = randint(100, 200)
    project_id = randint(1000, 2000)
    group = create_model_group_record(db, user_id, project_id)

    model_hash = random_hash("dataset")
    model_in = ModelCreate(
        db=db,
        hash=model_hash,
        source=1,
        type=1,
        user_id=user_id,
        task_id=1,
        model_group_id=group.id,
        project_id=project_id,
    )
    model = crud.model.create_with_version(db=db, obj_in=model_in)
    assert model.hash == model_hash
    assert model.name == f"{group.name}_1"


def test_get_model(db: Session) -> None:
    user_id = randint(100, 200)
    project_id = randint(1000, 2000)
    group = create_model_group_record(db, user_id, project_id)

    model_hash = random_hash("model")
    model_in = ModelCreate(
        db=db,
        hash=model_hash,
        source=1,
        type=1,
        user_id=user_id,
        task_id=1,
        model_group_id=group.id,
        project_id=project_id,
    )
    model = crud.model.create_with_version(db=db, obj_in=model_in)
    stored_model = crud.model.get(db=db, id=model.id)

    assert model.hash == stored_model.hash
    assert model.name == stored_model.name


def test_delete_model(db: Session):
    model_hash = random_hash("model")
    model_in = ModelCreate(
        db=db,
        hash=model_hash,
        type=1,
        source=1,
        user_id=1,
        task_id=1,
        model_group_id=randint(1000, 2000),
        project_id=randint(2001, 3000),
    )
    model = crud.model.create_with_version(db=db, obj_in=model_in)
    stored_model = crud.model.get(db=db, id=model.id)

    assert not stored_model.is_deleted

    model = crud.model.soft_remove(db, id=model.id)
    deleted_model = crud.model.get(db=db, id=model.id)
    assert deleted_model.is_deleted
