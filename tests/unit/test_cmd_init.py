import os
import shutil
import unittest

from tests import utils as test_utils

from mir.commands import init


class TestCmdInit(unittest.TestCase):
    def test_init(self):
        test_root = test_utils.dir_test_root(self.id().split(".")[-3:])
        if os.path.isdir(test_root):
            shutil.rmtree(test_root)
        os.makedirs(test_root)
        init.CmdInit.run_with_args(test_root)
        assert (os.path.isdir(os.path.join(test_root, ".git")))
        assert (os.path.isdir(os.path.join(test_root, ".dvc")))
