from typing import Any
from random import randint
from app.libs import datasets as m
from tests.utils.utils import random_lower_string


class TestImportDatasetPaths:
    def test_import_dataset_paths(self, mocker: Any, tmp_path: Any) -> None:
        input_path = tmp_path
        m.settings.SHARED_DATA_DIR = str(tmp_path)
        (tmp_path / "images").mkdir()
        (tmp_path / "pred").mkdir()
        p = m.ImportDatasetPaths(input_path, random_lower_string())
        assert p.pred_dir == str(input_path / "pred")
        assert p.asset_dir == str(input_path / "images")
        assert p.gt_dir is None


class TestEvaluateDataset:
    def test_evaluate_datasets(self, mocker: Any) -> None:
        user_id = randint(100, 200)
        project_id = randint(1000, 2000)
        confidence_threshold = 0.233
        iou = 0.5
        require_average_iou = True
        need_pr_curve = True
        ctrl = mocker.Mock(evaluate_dataset=mocker.Mock(return_value={}))
        datasets_mapping = {"a": 1, "b": 2}
        m.evaluate_datasets(
            ctrl,
            user_id,
            project_id,
            confidence_threshold,
            iou,
            require_average_iou,
            need_pr_curve,
            "main_ck",
            datasets_mapping,
        )

        ctrl.evaluate_dataset.assert_called()
