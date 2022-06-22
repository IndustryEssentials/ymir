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
    def test_evaluate_datasets(self, mocker: Any) -> None:
        user_id = randint(100, 200)
        project_id = randint(1000, 2000)
        confidence_threshold = 0.233
        iou = 0.5
        require_average_iou = True
        ctrl = mocker.Mock()
        viz = mocker.Mock()
        viz.get_fast_evaluation.return_value = {}
        user_labels = mocker.Mock()
        datasets = [mocker.Mock()]
        m.evaluate_datasets(
            ctrl, viz, user_id, project_id, user_labels, confidence_threshold, iou, require_average_iou, datasets
        )

        viz.get_fast_evaluation.assert_called()
