from pathlib import Path

import pytest
from app.utils import files as m
from tests.utils.utils import random_url


class TestPreprocessingDataset:
    def test_preprocess_dataset(self, tmp_path, mocker):
        output_dir = tmp_path / "import_dataset"
        output_dir.mkdir()

        mocker.patch.object(m, "download_file", return_value=b"")
        mocker.patch.object(m, "decompress_zip", return_value=None)
        mocker.patch.object(m, "locate_dir", return_value=Path("./a/b"))
        mocker.patch.object(m, "locate_annotation_dir", return_value=None)
        url = random_url()
        asset_dir, gt_dir, pred_dir = m.prepare_downloaded_paths(url, output_dir)
        assert asset_dir == Path("a/b")
        assert gt_dir is None
        assert pred_dir is None


class TestIsRelativeTo:
    def test_is_relative_to(self):
        a = Path("/x/y/z")
        b = Path("/x/")
        assert m.is_relative_to(a, b)
        assert not m.is_relative_to(b, a)


class TestIsValidImportPath:
    def test_locate_import_paths(self, mocker, tmp_path):
        asset_dir = tmp_path / "images"
        asset_dir.mkdir()
        m.settings.SHARED_DATA_DIR = str(tmp_path)
        ret_asset_dir, gt_dir, pred_dir = m.locate_import_paths(tmp_path)
        assert ret_asset_dir == asset_dir
        assert gt_dir is None
        assert pred_dir is None

    def test_locate_import_paths_error(self, mocker, tmp_path):
        m.settings.SHARED_DATA_DIR = str(tmp_path)
        with pytest.raises(FileNotFoundError):
            m.locate_import_paths(tmp_path)
