import pytest
from datetime import datetime
from random import randint
from typing import Any

from sqlalchemy.orm import Session

from app.libs import tasks as m
from tests.utils.utils import random_lower_string
from app.constants.state import TaskType
from tests.utils.tasks import create_task
from tests.utils.datasets import create_dataset_record, create_dataset_group_record
from tests.utils.models import create_model_group_record


class TestCreateSingleTask:
    def test_create_single_task(self, db: Session, mocker: Any) -> None:
        ctrl = mocker.Mock()
        dataset = mocker.Mock(id=randint(100, 200), hash=random_lower_string(), create_datetime=datetime.now())
        dataset.name = random_lower_string()
        mocker.patch.object(m, "ControllerClient", return_value=ctrl)
        mocker.patch.object(m, "ensure_datasets_are_ready", return_value=[dataset])
        user_id = randint(100, 200)
        project_id = randint(1000, 2000)
        user_labels = mocker.Mock()
        j = {
            "name": random_lower_string(),
            "type": TaskType.training.value,
            "project_id": project_id,
            "parameters": {"dataset_id": dataset.id, "task_type": "training", "project_id": project_id},
        }
        task_in = m.schemas.TaskCreate(**j)
        task = m.create_single_task(db, user_id, user_labels, task_in)
        assert task.type == TaskType.training
        assert task.project_id == project_id
        ctrl.create_task.assert_called()


class TestTaskResult:
    def test_task_result_propriety(self, db: Session, mocker: Any) -> None:
        user_id = randint(100, 200)
        project_id = randint(1000, 2000)
        task_in_db = create_task(db, user_id, project_id)

        ctrl = mocker.Mock()
        mocker.patch.object(m, "ControllerClient", return_value=ctrl)
        viz = mocker.MagicMock()
        mocker.patch.object(m, "VizClient", return_value=viz)

        tr = m.TaskResult(db, task_in_db)
        ctrl.get_labels_of_user.assert_not_called()
        viz.get_model_info.assert_not_called()
        viz.get_dataset_info.assert_not_called()

        tr.user_labels
        ctrl.get_labels_of_user.assert_called()

        tr.model_info()
        viz.get_model_info.assert_called()
        tr.dataset_info()
        viz.get_dataset_info.assert_called()

    def test_get_dest_group_info_is_dataset(self, db: Session, mocker: Any) -> None:
        user_id = randint(100, 200)
        project_id = randint(1000, 2000)
        task_in_db = create_task(db, user_id, project_id)

        ctrl = mocker.Mock()
        mocker.patch.object(m, "ControllerClient", return_value=ctrl)
        viz = mocker.Mock()
        mocker.patch.object(m, "VizClient", return_value=viz)

        tr = m.TaskResult(db, task_in_db)
        group = create_dataset_group_record(db, user_id, project_id)
        dataset = create_dataset_record(db, user_id, project_id, dataset_group_id=group.id)

        result_group_id = tr.get_dest_group_id(dataset.id, group.id, group.name)
        assert group.id == result_group_id

    def test_get_dest_group_info_is_model(self, db: Session, mocker: Any) -> None:
        user_id = randint(100, 200)
        project_id = randint(1000, 2000)
        task_in_db = create_task(db, user_id, project_id, type_=TaskType.training)

        ctrl = mocker.Mock()
        mocker.patch.object(m, "ControllerClient", return_value=ctrl)
        viz = mocker.Mock()
        mocker.patch.object(m, "VizClient", return_value=viz)

        tr = m.TaskResult(db, task_in_db)
        dataset_group = create_dataset_group_record(db, user_id, project_id)
        dataset = create_dataset_record(db, user_id, project_id, dataset_group_id=dataset_group.id)
        model_group = create_model_group_record(db, user_id, project_id, dataset.id)

        result_group_id = tr.get_dest_group_id(dataset.id, model_group.id, model_group.name)
        assert model_group.id == result_group_id


class TestShouldRetry:
    @pytest.mark.asyncio()
    async def test_should_retry(self, mocker: Any) -> None:
        resp = mocker.AsyncMock(ok=False)
        assert await m.should_retry(resp)

        resp = mocker.AsyncMock(ok=True)
        assert not await m.should_retry(resp)
