import os
import shutil
import unittest

from tests import utils as test_utils

from mir.commands import init
from mir.tools import class_ids


class TestCmdInit(unittest.TestCase):
    def test_init(self):
        test_root = test_utils.dir_test_root(self.id().split(".")[-3:])

        if os.path.isdir(test_root):
            shutil.rmtree(test_root)
        os.makedirs(test_root)
        init.CmdInit.run_with_args(test_root)

        assert (os.path.isdir(os.path.join(test_root, ".git")))
        assert (os.path.isdir(os.path.join(test_root, ".dvc")))
        assert os.path.isfile(os.path.join(test_root, class_ids.ids_file_name()))
        ignore_file_path = os.path.join(test_root, '.gitignore')
        assert os.path.isfile(ignore_file_path)
        with open(ignore_file_path, 'r') as f:
            lines = f.read().splitlines()
        assert class_ids.ids_file_name() in lines
