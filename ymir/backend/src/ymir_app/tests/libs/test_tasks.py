import pytest
from random import randint
from typing import Any

from sqlalchemy.orm import Session

from app.libs import tasks as m
from tests.utils.utils import random_lower_string
from common_utils.labels import UserLabels
from app.constants.state import TaskType
from tests.utils.tasks import create_task
from tests.utils.datasets import create_dataset_record, create_dataset_group_record
from tests.utils.models import create_model_group_record


class TestNormalizeParameters:
    def test_normalize_task_parameters_succeed(self, mocker: Any) -> Any:
        mocker.patch.object(m, "crud")
        params = {
            "keywords": "cat,dog,boy".split(","),
            "dataset_id": 1,
            "model_id": 233,
            "name": random_lower_string(5),
            "else": None,
        }
        user_labels = UserLabels.parse_obj(
            dict(
                labels=[
                    {
                        "name": "cat",
                        "aliases": [],
                        "create_time": 1647075205.0,
                        "update_time": 1647075206.0,
                        "id": 0,
                    },
                    {
                        "id": 1,
                        "name": "dog",
                        "aliases": [],
                        "create_time": 1647076207.0,
                        "update_time": 1647076408.0,
                    },
                    {
                        "id": 2,
                        "name": "boy",
                        "aliases": [],
                        "create_time": 1647076209.0,
                        "update_time": 1647076410.0,
                    },
                ]
            )
        )
        params = m.schemas.TaskParameter(**params)
        res = m.normalize_parameters(mocker.Mock(), params, None, user_labels)
        assert res["class_ids"] == [0, 1, 2]
        assert "dataset_hash" in res
        assert "model_hash" in res


class TestWriteClickhouseMetrics:
    def test_write_clickhouse_metrics(self, mocker: Any) -> None:
        ch = mocker.Mock()
        mocker.patch.object(m, "YmirClickHouse", return_value=ch)
        task_info = mocker.Mock(type=TaskType.training.value)
        dataset_id = randint(100, 200)
        dataset_group_id = randint(1000, 2000)
        model_id = randint(10000, 20000)
        keywords = [random_lower_string() for _ in range(3)]

        m.write_clickhouse_metrics(task_info, dataset_group_id, dataset_id, model_id, keywords)
        ch.save_task_parameter.assert_called()
        ch.save_dataset_keyword.assert_called()


class TestCreateSingleTask:
    def test_create_single_task(self, db: Session, mocker: Any) -> None:
        mocker.patch.object(m, "normalize_parameters")
        ctrl = mocker.Mock()
        mocker.patch.object(m, "ControllerClient", return_value=ctrl)
        mocker.patch.object(m, "YmirClickHouse")
        user_id = randint(100, 200)
        project_id = randint(1000, 2000)
        user_labels = mocker.Mock()
        j = {
            "name": random_lower_string(),
            "type": TaskType.training.value,
            "project_id": project_id,
            "parameters": {"dataset_id": randint(100, 200)},
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
        viz = mocker.Mock()
        mocker.patch.object(m, "VizClient", return_value=viz)

        tr = m.TaskResult(db, task_in_db)
        ctrl.get_labels_of_user.assert_not_called()
        viz.get_model.assert_not_called()
        viz.get_dataset.assert_not_called()

        tr.user_labels
        ctrl.get_labels_of_user.assert_called()

        tr.model_info
        viz.get_model.assert_called()
        tr.dataset_info
        viz.get_dataset.assert_called()

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

        result_group_id, result_group_name = tr.get_dest_group_info(dataset.id)
        assert group.id == result_group_id
        assert group.name == result_group_name

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

        result_group_id, result_group_name = tr.get_dest_group_info(dataset.id)
        assert model_group.id == result_group_id
        assert model_group.name == result_group_name


class TestShouldRetry:
    @pytest.mark.asyncio()
    async def test_should_retry(self, mocker: Any) -> None:
        resp = mocker.Mock(ok=False)
        assert await m.should_retry(resp)

        resp = mocker.Mock(ok=True)
        assert not await m.should_retry(resp)
