import os
import shutil
import unittest

from google.protobuf.json_format import ParseDict

from mir.commands.show import CmdShow
from mir.protos import mir_command_pb2 as mirpb
from mir.tools.code import MirCode
from tests import utils as test_utils


class TestCmdShow(unittest.TestCase):
    def _prepare_mir_repo_branch_mining(self, mir_repo_root):
        mir_annotations = mirpb.MirAnnotations()
        mir_keywords = mirpb.MirKeywords()
        mir_metadatas = mirpb.MirMetadatas()
        mir_tasks = mirpb.MirTasks()

        dict_metadatas = {
            'attributes': {
                'd4e4a60147f1e35bc7f5bc89284aa16073b043c9': {
                    'assetType': 'AssetTypeImageJpeg',
                    'width': 1080,
                    'height': 1620,
                    'imageChannels': 3
                }
            }
        }
        ParseDict(dict_metadatas, mir_metadatas)

        dict_tasks = {
            'tasks': {
                '5928508c-1bc0-43dc-a094-0352079e39b5': {
                    'type': 'TaskTypeMining',
                    'name': 'mining',
                    'task_id': 'mining-task-id',
                    'timestamp': '1624376173'
                }
            }
        }
        ParseDict(dict_tasks, mir_tasks)

        test_utils.mir_repo_commit_all(mir_repo_root, mir_metadatas, mir_annotations, mir_keywords, mir_tasks,
                                       "prepare_branch_status")

    def test_show_00(self):
        mir_root = test_utils.dir_test_root(self.id().split(".")[-3:])
        if os.path.isdir(mir_root):
            shutil.rmtree(mir_root)
        os.makedirs(mir_root)

        test_utils.mir_repo_init(mir_root)
        # prepare branch a
        test_utils.mir_repo_create_branch(mir_root, "a")
        self._prepare_mir_repo_branch_mining(mir_root)

        args = type('', (), {})()
        args.mir_root = mir_root
        args.verbose = False
        args.src_revs = "a@5928508c-1bc0-43dc-a094-0352079e39b5"
        cmd_instance = CmdShow(args)
        ret = cmd_instance.run()
        assert ret == MirCode.RC_OK

        args = type('', (), {})()
        args.mir_root = mir_root
        args.verbose = True
        args.src_revs = "a@5928508c-1bc0-43dc-a094-0352079e39b5"
        cmd_instance = CmdShow(args)
        ret = cmd_instance.run()
        assert ret == MirCode.RC_OK
