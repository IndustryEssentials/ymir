from random import randint

from sqlalchemy.orm import Session

from app import crud
from app.schemas.model import ModelCreate
from app.constants.state import ResultState
from tests.utils.utils import random_hash
from tests.utils.models import create_model_group_record, create_model


def test_create_model(db: Session) -> None:
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


class TestToggleModelVisibility:
    def test_toggle_model(self, db: Session) -> None:
        user_id = randint(100, 200)
        project_id = randint(1000, 2000)
        model = create_model(db, user_id, project_id)
        assert model.is_visible

        crud.model.batch_toggle_visibility(db, ids=[model.id], action="hide")
        model = crud.model.get(db, id=model.id)
        assert not model.is_visible

        crud.model.batch_toggle_visibility(db, ids=[model.id], action="unhide")
        model = crud.model.get(db, id=model.id)
        assert model.is_visible


class TestDeleteModelGroupResources:
    def test_delete_model_group_resources(self, db: Session) -> None:
        user_id = randint(100, 200)
        project_id = randint(1000, 2000)
        group = create_model_group_record(db, user_id, project_id)
        model1 = create_model(db, user_id, group.id, project_id)
        model2 = create_model(db, user_id, group.id, project_id)
        assert not model1.is_deleted
        assert not model2.is_deleted

        crud.model.remove_group_resources(db, group_id=group.id)
        assert model1.is_deleted
        assert model2.is_deleted


class TestUpdateModelState:
    def test_update_model_state(self, db: Session) -> None:
        user_id = randint(100, 200)
        project_id = randint(1000, 2000)
        model = create_model(db, user_id, project_id)
        assert model.result_state == ResultState.processing

        crud.model.update_state(db, model_id=model.id, new_state=ResultState.ready)
        assert model.result_state == ResultState.ready
