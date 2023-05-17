import os
import shutil
import unittest

from tests import utils as test_utils

from mir.commands import init
from mir.protos import mir_command_pb2 as mirpb
from mir.tools import class_ids, mir_storage_ops


class TestCmdInit(unittest.TestCase):
    def test_init(self):
        test_root = test_utils.dir_test_root(self.id().split(".")[-3:])

        # create mir root
        if os.path.isdir(test_root):
            shutil.rmtree(test_root)
        os.makedirs(test_root)
        label_storage_file = class_ids.ids_file_path(test_root)

        init.CmdInit.run_with_args(mir_root=test_root, label_storage_file=label_storage_file, empty_rev='a@a')

        assert (os.path.isdir(os.path.join(test_root, ".git")))
        assert (os.path.isdir(os.path.join(test_root, ".mir")))
        assert os.path.isfile(class_ids.ids_file_path(mir_root=test_root))
        ignore_file_path = os.path.join(test_root, '.gitignore')
        assert os.path.isfile(ignore_file_path)
        with open(ignore_file_path, 'r') as f:
            lines = f.read().splitlines()
        assert '.mir' in lines

        mir_annotations: mirpb.MirAnnotations = mir_storage_ops.MirStorageOps.load_single_storage(
            mir_root=test_root, mir_branch='a', mir_task_id='a', ms=mirpb.MirStorage.MIR_ANNOTATIONS)
        assert(mir_annotations.prediction.type == mirpb.ObjectType.OT_NO_ANNOTATIONS)
        assert(mir_annotations.ground_truth.type == mirpb.ObjectType.OT_NO_ANNOTATIONS)
