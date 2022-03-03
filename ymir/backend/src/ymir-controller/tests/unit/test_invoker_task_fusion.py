import os
import shutil
import unittest
from unittest import mock

from controller.utils import utils
from controller.utils.invoker_call import make_invoker_cmd_call
from controller.utils.invoker_mapping import RequestTypeToInvoker
from proto import backend_pb2
import tests.utils as test_utils


RET_ID = 'done'


class TestInvokerTaskFusion(unittest.TestCase):
    # life cycle
    def __init__(self, methodName: str = ...) -> None:
        # dir structure:
        # test_involer_CLSNAME_sandbox_root
        # ├── media_storage_root
        # └── user
        #     └── repoid
        super().__init__(methodName)
        self._user_name = "user"
        self._mir_repo_name = "repoid"
        self._storage_name = "media_storage_root"
        self._task_id = 't000aaaabbbbbbzzzzzzzzzzzzzzd5'
        self._sub_task_id_0 = utils.sub_task_id(self._task_id, 0)
        self._sub_task_id_1 = utils.sub_task_id(self._task_id, 1)
        self._sub_task_id_2 = utils.sub_task_id(self._task_id, 2)
        self._guest_id1 = 't000aaaabbbbbbzzzzzzzzzzzzzzz1'
        self._guest_id2 = 't000aaaabbbbbbzzzzzzzzzzzzzzz2'

        self._sandbox_root = test_utils.dir_test_root(self.id().split(".")[-3:])
        self._user_root = os.path.join(self._sandbox_root, self._user_name)
        self._mir_repo_root = os.path.join(self._user_root, self._mir_repo_name)
        self._storage_root = os.path.join(self._sandbox_root, self._storage_name)

        self._work_dir = os.path.join(self._sandbox_root, "work_dir",
                                      backend_pb2.TaskType.Name(backend_pb2.TaskTypeFusion), self._task_id)
        self._sub_work_dir_0 = os.path.join(self._work_dir, 'sub_task', self._sub_task_id_0)
        self._sub_work_dir_1 = os.path.join(self._work_dir, 'sub_task', self._sub_task_id_1)
        self._sub_work_dir_2 = os.path.join(self._work_dir, 'sub_task', self._sub_task_id_2)

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
        os.makedirs(self._sub_work_dir_0, exist_ok=True)
        os.makedirs(self._sub_work_dir_1, exist_ok=True)
        os.makedirs(self._sub_work_dir_2, exist_ok=True)

    def _prepare_mir_repo(self):
        test_utils.mir_repo_init(self._mir_repo_root)

    # protected: mocked
    def _mock_run_func(*args, **kwargs):
        ret = type('', (), {})()
        ret.returncode = 0
        ret.stdout = RET_ID
        return ret

    # public: test cases
    @mock.patch("subprocess.run", side_effect=_mock_run_func)
    def test_invoker_00(self, mock_run):
        req_create_task = backend_pb2.ReqCreateTask()
        req_create_task.task_type = backend_pb2.TaskTypeFusion
        req_create_task.no_task_monitor = True

        req_create_task.fusion.in_dataset_ids.extend([self._guest_id1, self._guest_id2])
        req_create_task.fusion.merge_strategy = backend_pb2.MergeStrategy.HOST
        req_create_task.fusion.in_class_ids.extend([1, 3, 5])
        req_create_task.fusion.ex_class_ids.extend([2, 4])
        req_create_task.fusion.count = 100

        expected_merge_cmd = "mir merge "
        expected_filter_cmd = "mir filter "
        expected_sampling_cmd = "mir sampling"
        mock_run.assert_has_calls(calls=[
            mock.call(expected_merge_cmd.split(' '), capture_output=True, text=True),
            mock.call(expected_filter_cmd.split(' '), capture_output=True, text=True),
            mock.call(expected_sampling_cmd.split(' '), capture_output=True, text=True),
        ])
