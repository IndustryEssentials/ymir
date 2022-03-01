import os
import shutil
import unittest

import yaml

from tests import utils as test_utils

from mir.commands import init
from mir.tools import class_ids


class TestCmdInit(unittest.TestCase):
    def test_init(self):
        test_root = test_utils.dir_test_root(self.id().split(".")[-3:])

        # create mir root
        if os.path.isdir(test_root):
            shutil.rmtree(test_root)
        os.makedirs(test_root)
        # write labels.csv
        with open(os.path.join(test_root, 'labels.csv'), 'w') as f:
            f.write('0,,xbox\n1,,person\n2,,cat\n')

        init.CmdInit.run_with_args(mir_root=test_root, project_class_names='cat;person')

        assert (os.path.isdir(os.path.join(test_root, ".git")))
        assert (os.path.isdir(os.path.join(test_root, ".dvc")))
        assert os.path.isfile(os.path.join(test_root, class_ids.ids_file_name()))
        ignore_file_path = os.path.join(test_root, '.gitignore')
        assert os.path.isfile(ignore_file_path)
        with open(ignore_file_path, 'r') as f:
            lines = f.read().splitlines()
        assert class_ids.ids_file_name() in lines
        assert '.mir' in lines

        # check project context file
        project_context_file_path = os.path.join(test_root, '.mir', 'context.yaml')
        assert os.path.isfile(project_context_file_path)
        with open(project_context_file_path, 'r') as f:
            context_obj = yaml.safe_load(f)
            assert context_obj['project']['class_ids'] == [2, 1]
