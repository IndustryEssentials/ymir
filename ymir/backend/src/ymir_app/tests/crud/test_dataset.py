from random import randint

from sqlalchemy.orm import Session

from app import crud
from app.schemas.dataset import DatasetCreate
from tests.utils.utils import random_hash
from tests.utils.dataset_groups import create_dataset_group_record


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
