from random import randint
from typing import Any

from sqlalchemy.orm import Session

from app.libs import iterations as m
from tests.utils.datasets import create_dataset_record
from tests.utils.projects import create_project_record
from tests.utils.iterations import create_iteration_record


class TestCalculateMiningProgress:
    def test_calculate_mining_progress(self, db: Session, mocker: Any) -> None:
        project = create_project_record(db)
        dataset = create_dataset_record(db, user_id=project.user_id, project_id=project.id)
        iteration = create_iteration_record(db, project.user_id, project.id, mining_dataset_id=dataset.id)

        id_for_names = mocker.Mock(return_value=([randint(1, 10)] * 3,))
        user_labels = mocker.Mock(id_for_names=id_for_names)

        mocker.patch.object(m, "VizClient")
        res = m.calculate_mining_progress(db, user_labels, project.user_id, project.id, iteration.id)
        assert "total_mining_ratio" in res
        assert "class_wise_mining_ratio" in res
        assert "negative_ratio" in res


class TestGetTrainingClasses:
    def test_get_training_classes(self, db: Session, mocker: Any) -> None:
        project = create_project_record(db)
        id_for_names = mocker.Mock(return_value=([randint(1, 10)] * 3,))
        user_labels = mocker.Mock(id_for_names=id_for_names)
        classes = m.get_training_classes(db, project.id, user_labels)
        assert list(classes.keys()) == project.training_targets
