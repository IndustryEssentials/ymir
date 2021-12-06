from pathlib import Path

from app.utils import files as m
from tests.utils.utils import random_url


class TestPreprocessingDataset:
    def test_preprocess_dataset(self, tmp_path, mocker):
        output_dir = tmp_path / "import_dataset"
        output_dir.mkdir()

        mocker.patch.object(m, "download_file", return_value=b"")
        mocker.patch.object(m, "decompress_zip", return_value=None)
        mocker.patch.object(
            m, "locate_dirs", return_value=iter([("images", ""), ("annotations", "")])
        )
        url = random_url()
        ret = m.prepare_dataset(url, output_dir)
        assert "images" in ret
        assert "annotations" in ret


class TestIsRelativeTo:
    def test_is_relative_to(self):
        a = Path("/x/y/z")
        b = Path("/x/")
        assert m.is_relative_to(a, b)
        assert not m.is_relative_to(b, a)
