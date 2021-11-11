import os
import shutil
import unittest

from mir.commands import copy
from mir.protos import mir_command_pb2 as mirpb
from mir.tools import mir_storage, mir_storage_ops
from mir.tools.code import MirCode

from tests import utils as test_utils


class TestCmdCopy(unittest.TestCase):
    # lifecycle
    def __init__(self, methodName: str) -> None:
        super().__init__(methodName=methodName)
        self._test_root = test_utils.dir_test_root(self.id().split(".")[-3:])
        self._mir_root = os.path.join(self._test_root, 'one')
        self._src_mir_root = os.path.join(self._test_root, 'another')
        self._work_dir = os.path.join(self._test_root, 'work_dir')

    def setUp(self) -> None:
        self.__prepare_dir()
        self.__prepare_mir()
        self.__prepare_src_mir()
        return super().setUp()

    def tearDown(self) -> None:
        self.__deprepare_dir()
        return super().tearDown()

    # private: prepare
    def __prepare_dir(self):
        test_utils.remake_dirs(self._test_root)
        test_utils.remake_dirs(self._mir_root)
        test_utils.remake_dirs(self._src_mir_root)
        test_utils.remake_dirs(self._work_dir)

    def __deprepare_dir(self):
        if os.path.isdir(self._test_root):
            shutil.rmtree(self._test_root)

    def __prepare_mir(self):
        test_utils.mir_repo_init(self._mir_root)

    def __prepare_src_mir(self):
        test_utils.mir_repo_init(self._src_mir_root)

        test_utils.mir_repo_create_branch(self._src_mir_root, 'a')

        mir_metadatas = mirpb.MirMetadatas()
        mir_metadatas.attributes['asset0']
        mir_metadatas.attributes['asset1']

        mir_annotations = mirpb.MirAnnotations()
        mir_annotations.head_task_id = 't0'
        mir_annotations.task_annotations['t0']

        mir_tasks = mirpb.MirTasks()
        mir_tasks.head_task_id = 't0'
        mir_tasks.tasks['t0']
        mir_tasks.tasks['t0'].type = mirpb.TaskTypeTraining
        mir_tasks.tasks['t0'].model.mean_average_precision = 0.3

        test_utils.mir_repo_commit_all(mir_root=self._src_mir_root,
                                       mir_metadatas=mir_metadatas,
                                       mir_annotations=mir_annotations,
                                       mir_keywords=mirpb.MirKeywords(),
                                       mir_tasks=mir_tasks,
                                       no_space_message="commit for src branch a")

    # public: test cases
    def test_normal_00(self):
        # run cmd
        fake_args = type('', (), {})()
        fake_args.mir_root = self._mir_root
        fake_args.src_mir_root = self._src_mir_root
        fake_args.src_revs = 'a@t0'
        fake_args.dst_rev = 'b@t1'
        fake_args.work_dir = self._work_dir
        cmd_copy = copy.CmdCopy(fake_args)
        return_code = cmd_copy.run()

        # check result
        self.assertEqual(MirCode.RC_OK, return_code)

        mir_datas = mir_storage_ops.MirStorageOps.load(mir_root=self._mir_root,
                                                       mir_branch='b',
                                                       mir_storages=mir_storage.get_all_mir_storage())
        metadatas_keys = set(mir_datas[mirpb.MIR_METADATAS].attributes.keys())
        self.assertEqual({'asset0', 'asset1'}, metadatas_keys)
        self.assertEqual('t1', mir_datas[mirpb.MIR_ANNOTATIONS].head_task_id)
        self.assertEqual('t1', mir_datas[mirpb.MIR_TASKS].head_task_id)
        mAP = mir_datas[mirpb.MIR_TASKS].tasks['t1'].model.mean_average_precision
        self.assertTrue(mAP > 0.29999 and mAP < 0.30001)  # it's actually 0.3
