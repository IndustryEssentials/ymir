import logging
import os
import shutil
import unittest
from unittest import mock

from common_utils.labels import UserLabels
from controller.utils.invoker_call import make_invoker_cmd_call
from controller.utils.invoker_mapping import RequestTypeToInvoker
from mir.protos import mir_command_pb2 as mir_cmd_pb
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
        self._guest_id1 = 't000aaaabbbbbbzzzzzzzzzzzzzzz1'
        self._guest_id2 = 't000aaaabbbbbbzzzzzzzzzzzzzzz2'
        self._guest_id3 = 't000aaaabbbbbbzzzzzzzzzzzzzzz3'

        self._sandbox_root = test_utils.dir_test_root(self.id().split(".")[-3:])
        self._user_root = os.path.join(self._sandbox_root, self._user_name)
        self._mir_repo_root = os.path.join(self._user_root, self._mir_repo_name)
        self._storage_root = os.path.join(self._sandbox_root, self._storage_name)

        self._work_dir = os.path.join(self._sandbox_root, "work_dir",
                                      mir_cmd_pb.TaskType.Name(mir_cmd_pb.TaskType.TaskTypeFusion), self._task_id)
        self._sub_work_dir_0 = os.path.join(self._work_dir, 'sub_task', self._task_id)

    def setUp(self) -> None:
        test_utils.check_commands()
        self._prepare_dirs()
        self._prepare_mir_repo()
        UserLabels.main_name_for_ids = mock.Mock(return_value=["person", "cat", "table"])
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
        req_create_task.task_type = mir_cmd_pb.TaskType.TaskTypeFusion
        req_create_task.no_task_monitor = True

        in_dataset_ids = [self._guest_id1, self._guest_id2]
        ex_dataset_ids = [self._guest_id3]
        merge_strategy = backend_pb2.MergeStrategy.HOST
        in_class_ids = [1, 3, 5]
        sampling_count = 100

        work_dir_root = os.path.join(self._sandbox_root, "work_dir",
                                     mir_cmd_pb.TaskType.Name(mir_cmd_pb.TaskType.TaskTypeFusion), self._task_id)
        expected_work_dir = os.path.join(work_dir_root, 'sub_task', self._task_id)

        expected_fuse_cmd = [
            'mir', 'fuse', '--root', self._mir_repo_root, '--dst-rev', f"{self._task_id}@{self._task_id}", '-w',
            expected_work_dir, '--src-revs', f"{self._guest_id1};{self._guest_id2}", '-s', 'host', '--ex-src-revs',
            self._guest_id3, '--cis', 'person;cat;table', '--user-label-file',
            test_utils.user_label_file(self._sandbox_root,
                                       self._user_name), '--filter-anno-src', 'pred', '--count', '100'
        ]

        response = make_invoker_cmd_call(
            invoker=RequestTypeToInvoker[backend_pb2.TASK_CREATE],
            sandbox_root=self._sandbox_root,
            assets_config={},
            req_type=backend_pb2.TASK_CREATE,
            user_id=self._user_name,
            repo_id=self._mir_repo_name,
            task_id=self._task_id,
            req_create_task=req_create_task,
            in_dataset_ids=in_dataset_ids,
            ex_dataset_ids=ex_dataset_ids,
            annotation_type=mir_cmd_pb.AnnotationType.AT_PRED,
            merge_strategy=merge_strategy,
            in_class_ids=in_class_ids,
            sampling_count=sampling_count,
        )
        logging.info(response)

        mocked_index_call = test_utils.mocked_index_call(user_id=self._user_name,
                                                         repo_id=self._mir_repo_name,
                                                         task_id=self._task_id)
        mock_run.assert_has_calls(
            [mock.call(expected_fuse_cmd, capture_output=True, text=True, cwd=None), mocked_index_call])
