from typing import Any
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
