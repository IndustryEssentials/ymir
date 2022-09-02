import os
import shutil
import unittest
from unittest import mock

from controller.utils.invoker_call import make_invoker_cmd_call
from controller.utils.invoker_mapping import RequestTypeToInvoker
from proto import backend_pb2
from mir.protos import mir_command_pb2 as mir_cmd_pb

import tests.utils as test_utils


class TestInvokerCmdEvaluate(unittest.TestCase):
    # life cycle
    def __init__(self, methodName: str) -> None:
        # dir structure:
        # test_involer_CLSNAME_sandbox_root
        # ├── media_storage_root
        # └── test_user
        #     └── ymir-dvc-test
        super().__init__(methodName=methodName)
        self._user_name = "user"
        self._mir_repo_name = "repoid"
        self._storage_name = "media_storage_root"
        self._in_dataset_ids = ['t000aaaabbbbbbzzzzzzzzzzzzzzz1']
        self._gt_dataset_id = 't000aaaabbbbbbzzzzzzzzzzzzzzz2'
        self._task_id = 't000aaaabbbbbbzzzzzzzzzzzzzzz4'
        self._dst_dataset_id = 't000aaaabbbbbbzzzzzzzzzzzzzzz4'

        self._conf_thr = 0.3
        self._iou_thrs_interval = '0.5:1.0:0.05'

        self._sandbox_root = test_utils.dir_test_root(self.id().split(".")[-3:])
        self._user_root = os.path.join(self._sandbox_root, self._user_name)
        self._mir_repo_root = os.path.join(self._user_root, self._mir_repo_name)
        self._storage_root = os.path.join(self._sandbox_root, self._storage_name)

    def setUp(self) -> None:
        test_utils.check_commands()
        self._prepare_dirs()
        self._prepare_mir_repo()
        return super().setUp()

    def tearDown(self) -> None:
        if os.path.isdir(self._sandbox_root):
            shutil.rmtree(self._sandbox_root)
        return super().tearDown()

    # protected: setup and teardown
    def _prepare_dirs(self):
        if os.path.isdir(self._sandbox_root):
            shutil.rmtree(self._sandbox_root)
        os.makedirs(self._sandbox_root)
        os.mkdir(self._user_root)
        os.mkdir(self._mir_repo_root)
        os.mkdir(self._storage_root)

    def _prepare_mir_repo(self):
        # init repo
        test_utils.mir_repo_init(self._mir_repo_root)

    # protected: mocked
    def _mock_run_func(*args, **kwargs):
        return mir_cmd_pb.Evaluation()

    # public: test cases
    @mock.patch("controller.invoker.invoker_cmd_evaluate.det_evaluate_datasets", side_effect=_mock_run_func)
    def test_evaluate_00(self, mock_run):
        evaluate_config = mir_cmd_pb.EvaluateConfig()
        evaluate_config.conf_thr = self._conf_thr
        evaluate_config.iou_thrs_interval = self._iou_thrs_interval

        response = make_invoker_cmd_call(invoker=RequestTypeToInvoker[backend_pb2.CMD_EVALUATE],
                                         sandbox_root=self._sandbox_root,
                                         req_type=backend_pb2.CMD_EVALUATE,
                                         user_id=self._user_name,
                                         repo_id=self._mir_repo_name,
                                         task_id=self._task_id,
                                         in_dataset_ids=self._in_dataset_ids,
                                         singleton_op=self._gt_dataset_id,
                                         evaluate_config=evaluate_config)
        self.assertEqual(response.code, 0)
