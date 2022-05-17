from random import randint
from typing import Any

from sqlalchemy.orm import Session

from app.libs import projects as m
from app.constants.state import ResultState, TaskType
from tests.utils.utils import random_lower_string


class TestSetupDatasetAndGroup:
    def test_setup_dataset_and_group(self, db: Session, mocker: Any) -> None:
        ctrl = mocker.Mock()
        group_name = random_lower_string()
        user_id = randint(100, 200)
        project_id = randint(1000, 2000)
        task_type = TaskType.import_data

        dataset = m.setup_dataset_and_group(db, ctrl, group_name, project_id, user_id, task_type)
        assert dataset.result_state == ResultState.processing


class TestSetupModelAndGroup:
    def test_setup_model_and_group(self, db: Session, mocker: Any) -> None:
        ctrl = mocker.Mock()
        group_name = random_lower_string()
        user_id = randint(100, 200)
        project_id = randint(1000, 2000)
        task_type = TaskType.import_data

        model = m.setup_model_and_group(db, ctrl, group_name, project_id, user_id, task_type)
        assert model.result_state == ResultState.processing
