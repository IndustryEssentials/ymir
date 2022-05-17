from random import randint

from sqlalchemy.orm import Session

from app import crud
from app.schemas.dataset import DatasetCreate
from app.constants.state import ResultState
from tests.utils.utils import random_hash
from tests.utils.dataset_groups import create_dataset_group_record
from tests.utils.datasets import create_dataset_record


def test_create_dataset(db: Session) -> None:
    user_id = randint(100, 200)
    project_id = randint(1000, 2000)
    group = create_dataset_group_record(db, user_id, project_id)
    dataset_hash = random_hash("dataset")
    dataset_in = DatasetCreate(
        db=db,
        hash=dataset_hash,
        source=1,
        type=1,
        user_id=user_id,
        task_id=1,
        project_id=project_id,
        dataset_group_id=group.id,
    )
    dataset = crud.dataset.create_with_version(db=db, obj_in=dataset_in)
    assert dataset.hash == dataset_hash
    assert dataset.name == f"{group.name}_1"


def test_get_dataset(db: Session) -> None:
    user_id = randint(100, 200)
    project_id = randint(1000, 2000)
    group = create_dataset_group_record(db, user_id, project_id)

    dataset_hash = random_hash("dataset")
    dataset_in = DatasetCreate(
        db=db,
        hash=dataset_hash,
        source=1,
        type=1,
        user_id=user_id,
        task_id=1,
        project_id=project_id,
        dataset_group_id=group.id,
    )
    dataset = crud.dataset.create_with_version(db=db, obj_in=dataset_in)
    stored_dataset = crud.dataset.get_by_hash(db=db, hash_=dataset_hash)

    assert dataset.hash == stored_dataset.hash
    assert dataset.name == stored_dataset.name


class TestToggleVisibility:
    def test_toggle_dataset(self, db: Session) -> None:
        user_id = randint(100, 200)
        project_id = randint(1000, 2000)
        dataset = create_dataset_record(db, user_id, project_id)
        assert dataset.is_visible

        crud.dataset.batch_toggle_visibility(db, ids=[dataset.id], action="hide")
        dataset = crud.dataset.get(db, id=dataset.id)
        assert not dataset.is_visible

        crud.dataset.batch_toggle_visibility(db, ids=[dataset.id], action="unhide")
        dataset = crud.dataset.get(db, id=dataset.id)
        assert dataset.is_visible


class TestDeleteGroupResources:
    def test_delete_group_resources(self, db: Session) -> None:
        user_id = randint(100, 200)
        project_id = randint(1000, 2000)
        group = create_dataset_group_record(db, user_id, project_id)
        dataset1 = create_dataset_record(db, user_id, project_id, group.id)
        dataset2 = create_dataset_record(db, user_id, project_id, group.id)
        assert not dataset1.is_deleted
        assert not dataset2.is_deleted

        crud.dataset.remove_group_resources(db, group_id=group.id)
        assert dataset1.is_deleted
        assert dataset2.is_deleted


class TestUpdateDatasetState:
    def test_update_dataset_state(self, db: Session) -> None:
        user_id = randint(100, 200)
        project_id = randint(1000, 2000)
        dataset = create_dataset_record(db, user_id, project_id, state_=ResultState.processing)
        assert dataset.result_state == ResultState.processing

        crud.dataset.update_state(db, dataset_id=dataset.id, new_state=ResultState.ready)
        assert dataset.result_state == ResultState.ready
