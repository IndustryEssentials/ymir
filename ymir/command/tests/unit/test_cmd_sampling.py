import os
import shutil
import unittest

from google.protobuf import json_format

from mir.commands.sampling import CmdSampling
from mir.protos import mir_command_pb2 as mirpb
from mir.tools import mir_storage_ops
from mir.tools.code import MirCode

from tests import utils as test_utils


class TestCmdSampling(unittest.TestCase):
    # life cycle
    def __init__(self, methodName: str) -> None:
        super().__init__(methodName=methodName)
        self._mir_root = test_utils.dir_test_root(self.id().split(".")[-3:])

    def setUp(self) -> None:
        self.__prepare_dir(self._mir_root)
        self.__prepare_mir_repo(self._mir_root)
        return super().setUp()

    def tearDown(self) -> None:
        self.__deprepare_dir(self._mir_root)
        return super().tearDown()

    # private: prepare env
    def __prepare_dir(self, mir_root: str):
        if os.path.isdir(mir_root):
            shutil.rmtree(mir_root)
        os.makedirs(mir_root, exist_ok=True)

    def __deprepare_dir(self, mir_root: str):
        if os.path.isdir(mir_root):
            shutil.rmtree(mir_root)

    def __prepare_mir_repo(self, mir_root: str):
        test_utils.mir_repo_init(self._mir_root)

        metadatas_dict = {
            "attributes": {
                "a0000000000000000000000000000000000000000000000000": {
                    'assetType': 'AssetTypeImageJpeg',
                    'width': 1080,
                    'height': 1620,
                    'imageChannels': 3
                },
                "a0000000000000000000000000000000000000000000000001": {
                    'assetType': 'AssetTypeImageJpeg',
                    'width': 1080,
                    'height': 1620,
                    'imageChannels': 3
                },
                "a0000000000000000000000000000000000000000000000002": {
                    'assetType': 'AssetTypeImageJpeg',
                    'width': 1080,
                    'height': 1620,
                    'imageChannels': 3
                },
                "a0000000000000000000000000000000000000000000000003": {
                    'assetType': 'AssetTypeImageJpeg',
                    'width': 1080,
                    'height': 1620,
                    'imageChannels': 3
                },
                "a0000000000000000000000000000000000000000000000004": {
                    'assetType': 'AssetTypeImageJpeg',
                    'width': 1080,
                    'height': 1620,
                    'imageChannels': 3
                },
            }
        }
        mir_metadatas = mirpb.MirMetadatas()
        json_format.ParseDict(metadatas_dict, mir_metadatas)

        task = mir_storage_ops.create_task(task_type=mirpb.TaskType.TaskTypeImportData, task_id='t0', message='import')
        mir_storage_ops.MirStorageOps.save_and_commit(mir_root=self._mir_root,
                                                      mir_branch='a',
                                                      his_branch='master',
                                                      mir_datas={
                                                          mirpb.MirStorage.MIR_METADATAS: mir_metadatas,
                                                          mirpb.MirStorage.MIR_ANNOTATIONS: mirpb.MirAnnotations(),
                                                      },
                                                      task=task)

    def test_00(self):
        fake_args = type('', (), {})()
        fake_args.mir_root = self._mir_root
        fake_args.work_dir = ''
        fake_args.src_revs = 'a@t0'  # src branch name and base task id
        fake_args.dst_rev = 'b@t1'
        fake_args.count = 2
        fake_args.rate = 0
        cmd = CmdSampling(fake_args)
        cmd_run_result = cmd.run()

        # check result
        self.assertEqual(MirCode.RC_OK, cmd_run_result)
        mir_metadatas: mirpb.MirMetadatas = test_utils.read_mir_pb(os.path.join(self._mir_root, 'metadatas.mir'),
                                                                   mirpb.MirMetadatas)
        self.assertEqual(2, len(mir_metadatas.attributes))

        fake_args.count = 0
        fake_args.rate = 0.6
        fake_args.dst_rev = 'b@t2'
        cmd = CmdSampling(fake_args)
        cmd_run_result = cmd.run()

        # check result
        self.assertEqual(MirCode.RC_OK, cmd_run_result)
        mir_metadatas: mirpb.MirMetadatas = test_utils.read_mir_pb(os.path.join(self._mir_root, 'metadatas.mir'),
                                                                   mirpb.MirMetadatas)
        self.assertEqual(3, len(mir_metadatas.attributes))
