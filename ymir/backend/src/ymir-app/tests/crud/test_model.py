from random import randint
from sqlalchemy.orm import Session

from app import crud
from app.schemas.model import ModelCreate, ModelUpdate
from tests.utils.utils import random_hash, random_lower_string


def test_create_model(db: Session) -> None:
    model_name = random_lower_string(10)
    model_hash = random_hash("dataset")
    model_in = ModelCreate(
        db=db,
        name=model_name,
        hash=model_hash,
        type=1,
        user_id=1,
        task_id=1,
        model_group_id=randint(1000, 2000),
        project_id=randint(2001, 3000),
    )
    model = crud.model.create_with_version(db=db, obj_in=model_in)
    assert model.hash == model_hash
    assert model.name == model_name


def test_get_model(db: Session) -> None:
    model_name = random_lower_string(10)
    model_hash = random_hash("model")
    model_in = ModelCreate(
        db=db,
        name=model_name,
        hash=model_hash,
        type=1,
        user_id=1,
        task_id=1,
        model_group_id=randint(1000, 2000),
        project_id=randint(2001, 3000),
    )
    model = crud.model.create_with_version(db=db, obj_in=model_in)
    stored_model = crud.model.get(db=db, id=model.id)

    assert model.hash == stored_model.hash
    assert model.name == stored_model.name


def test_change_model_name(db: Session) -> None:
    model_name = random_lower_string(10)
    model_hash = random_hash("model")
    model_in = ModelCreate(
        db=db,
        name=model_name,
        hash=model_hash,
        type=1,
        user_id=1,
        task_id=1,
        model_group_id=randint(1000, 2000),
        project_id=randint(2001, 3000),
    )
    model = crud.model.create_with_version(db=db, obj_in=model_in)
    stored_model = crud.model.get(db=db, id=model.id)

    assert model.name == stored_model.name

    new_name = random_lower_string(10)
    model_update = ModelUpdate(name=new_name)
    model = crud.model.update(db, db_obj=model, obj_in=model_update)
    updated_model = crud.model.get(db=db, id=model.id)
    assert model.name == updated_model.name


def test_delete_model(db: Session):
    model_name = random_lower_string(10)
    model_hash = random_hash("model")
    model_in = ModelCreate(
        db=db,
        name=model_name,
        hash=model_hash,
        type=1,
        user_id=1,
        task_id=1,
        model_group_id=randint(1000, 2000),
        project_id=randint(2001, 3000),
    )
    model = crud.model.create_with_version(db=db, obj_in=model_in)
    stored_model = crud.model.get(db=db, id=model.id)

    assert model.name == stored_model.name
    assert not stored_model.is_deleted

    model = crud.model.soft_remove(db, id=model.id)
    deleted_model = crud.model.get(db=db, id=model.id)
    assert deleted_model.is_deleted
