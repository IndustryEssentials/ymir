import logging
import os
import shutil
import unittest
from unittest import mock

from common_utils import labels
from controller.utils import utils
from controller.utils.invoker_call import make_invoker_cmd_call
from controller.utils.invoker_mapping import RequestTypeToInvoker
from proto import backend_pb2
import tests.utils as test_utils

RET_ID = 'done'


class TestInvokerTaskFusion(unittest.TestCase):
    # life cycle
    def __init__(self, methodName: str) -> None:
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
        self._guest_id3 = 't000aaaabbbbbbzzzzzzzzzzzzzzz3'

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
        labels.UserLabels.get_main_names = mock.Mock(return_value=["person", "cat", "table"])
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
        req_create_task.fusion.ex_dataset_ids.extend([self._guest_id3])
        req_create_task.fusion.merge_strategy = backend_pb2.MergeStrategy.HOST
        req_create_task.fusion.in_class_ids.extend([1, 3, 5])
        req_create_task.fusion.count = 100

        work_dir_root = os.path.join(self._sandbox_root, "work_dir",
                                     backend_pb2.TaskType.Name(backend_pb2.TaskTypeFusion), self._task_id)
        expected_merge_work_dir = os.path.join(work_dir_root, 'sub_task', self._sub_task_id_2)
        expected_filter_work_dir = os.path.join(work_dir_root, 'sub_task', self._sub_task_id_1)
        expected_sampling_work_dir = os.path.join(work_dir_root, 'sub_task', self._sub_task_id_0)

        expected_merge_cmd = f"mir merge --root {self._mir_repo_root}"
        expected_merge_cmd += f" --dst-rev {self._task_id}@{self._sub_task_id_2} -s host"
        expected_merge_cmd += f" -w {expected_merge_work_dir}"
        expected_merge_cmd += f" --src-revs {self._guest_id1}@{self._guest_id1};{self._guest_id2}"
        expected_merge_cmd += f" --ex-src-revs {self._guest_id3}"

        expected_filter_cmd = f"mir filter --root {self._mir_repo_root}"
        expected_filter_cmd += f" --dst-rev {self._task_id}@{self._sub_task_id_1}"
        expected_filter_cmd += f" --src-revs {self._task_id}@{self._sub_task_id_2}"
        expected_filter_cmd += f" -w {expected_filter_work_dir} -p person;cat;table"

        expected_sampling_cmd = f"mir sampling --root {self._mir_repo_root}"
        expected_sampling_cmd += f" --dst-rev {self._task_id}@{self._task_id}"
        expected_sampling_cmd += f" --src-revs {self._task_id}@{self._sub_task_id_1}"
        expected_sampling_cmd += f" -w {expected_sampling_work_dir}"
        expected_sampling_cmd += ' --count 100'

        response = make_invoker_cmd_call(
            invoker=RequestTypeToInvoker[backend_pb2.TASK_CREATE],
            sandbox_root=self._sandbox_root,
            assets_config={},
            req_type=backend_pb2.TASK_CREATE,
            user_id=self._user_name,
            repo_id=self._mir_repo_name,
            task_id=self._task_id,
            req_create_task=req_create_task,
            merge_strategy=backend_pb2.MergeStrategy.HOST,
        )
        logging.info(response)

        mock_run.assert_has_calls(calls=[
            mock.call(expected_merge_cmd.split(' '), capture_output=True, text=True),
            mock.call(expected_filter_cmd.split(' '), capture_output=True, text=True),
            mock.call(expected_sampling_cmd.split(' '), capture_output=True, text=True),
        ])
