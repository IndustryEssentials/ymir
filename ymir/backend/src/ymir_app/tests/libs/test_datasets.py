from typing import Any
from random import randint
from app.libs import datasets as m
from tests.utils.utils import random_lower_string


class TestImportDatasetPaths:
    def test_import_dataset_paths(self, mocker: Any) -> None:
        mocker.patch.object(m, "verify_import_path", return_value=True)
        input_path = random_lower_string()
        p = m.ImportDatasetPaths(input_path, random_lower_string())
        assert p.annotation_dir == f"{input_path}/annotations"
        assert p.asset_dir == f"{input_path}/images"


class TestEvaluateDataset:
    def test_evaluate_dataset(self, mocker: Any) -> None:
        user_id = randint(100, 200)
        project_id = randint(1000, 2000)
        confidence_threshold = 0.233
        ctrl = mocker.Mock()
        viz = mocker.Mock()
        viz.get_evaluations.return_value = {}
        user_labels = mocker.Mock()
        gt_dataset = mocker.Mock()
        other_datasets = [mocker.Mock()]
        m.evaluate_dataset(
            ctrl, viz, user_id, project_id, user_labels, confidence_threshold, gt_dataset, other_datasets
        )

        ctrl.evaluate_dataset.assert_called()
        viz.get_evaluations.assert_called()
