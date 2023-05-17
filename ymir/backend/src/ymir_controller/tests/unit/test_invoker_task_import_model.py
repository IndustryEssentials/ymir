import logging
import os
import shutil
import unittest
from unittest import mock

from controller.utils.invoker_call import make_invoker_cmd_call
from controller.utils.invoker_mapping import RequestTypeToInvoker
from mir.protos import mir_command_pb2 as mir_cmd_pb
from proto import backend_pb2
import tests.utils as test_utils


class TestInvokerTaskImportModel(unittest.TestCase):
    # life cycle
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self._user_name = "user"
        self._mir_repo_name = "repoid"
        self._storage_name = "media_storage_root"
        self._task_id = 't000aaaabbbbbbzzzzzzzzzzzzzzd5'

        self._sandbox_root = test_utils.dir_test_root(self.id().split(".")[-3:])
        self._model_package_path = os.path.join(self._sandbox_root, 'model.tar.gz')
        self._user_root = os.path.join(self._sandbox_root, self._user_name)
        self._mir_repo_root = os.path.join(self._user_root, self._mir_repo_name)
        self._storage_root = os.path.join(self._sandbox_root, self._storage_name)
        self._assets_config = {
            'modelsuploadlocation': self._storage_root,
        }

    def setUp(self) -> None:
        self._prepare_dirs()
        self._prepare_fake_model()
        self._prepare_mir_repo()
        return super().setUp()

    def tearDown(self) -> None:
        self._deprepare_dirs()
        return super().tearDown()

    # protected: env prepare
    def _prepare_dirs(self):
        if os.path.isdir(self._sandbox_root):
            shutil.rmtree(self._sandbox_root)
        os.makedirs(self._sandbox_root)
        os.mkdir(self._user_root)
        os.mkdir(self._mir_repo_root)
        os.mkdir(self._storage_root)

    def _deprepare_dirs(self):
        if os.path.isdir(self._sandbox_root):
            shutil.rmtree(self._sandbox_root)

    def _prepare_fake_model(self):
        with open(self._model_package_path, 'w') as f:
            f.write('fake model package')

    def _prepare_mir_repo(self):
        test_utils.mir_repo_init(self._mir_repo_root)

    # protected: mocked
    def _mock_run_func(*args, **kwargs):
        ret = type('', (), {})()
        ret.returncode = 0
        ret.stdout = 'done'
        return ret

    # public: test cases
    @mock.patch("subprocess.run", side_effect=_mock_run_func)
    def test_invoker_00(self, mock_run):
        req_create_task = backend_pb2.ReqCreateTask()
        req_create_task.task_type = mir_cmd_pb.TaskType.TaskTypeImportModel
        req_create_task.no_task_monitor = True
        req_create_task.import_model.model_package_path = self._model_package_path

        response = make_invoker_cmd_call(invoker=RequestTypeToInvoker[backend_pb2.TASK_CREATE],
                                         sandbox_root=self._sandbox_root,
                                         assets_config=self._assets_config,
                                         req_type=backend_pb2.TASK_CREATE,
                                         user_id=self._user_name,
                                         repo_id=self._mir_repo_name,
                                         task_id=self._task_id,
                                         req_create_task=req_create_task)
        logging.info(f"import model response: {response}")
        work_dir_root = os.path.join(self._sandbox_root, "work_dir",
                                     mir_cmd_pb.TaskType.Name(mir_cmd_pb.TaskType.TaskTypeImportModel), self._task_id)
        working_dir_0 = os.path.join(work_dir_root, 'sub_task', self._task_id)
        expected_cmd = [
            'mir', 'models', '--root', self._mir_repo_root, '--package-path', self._model_package_path, '-w',
            working_dir_0, '--dst-rev', f"{self._task_id}@{self._task_id}", '--model-location', self._storage_root
        ]

        mocked_index_call = test_utils.mocked_index_call(user_id=self._user_name,
                                                         repo_id=self._mir_repo_name,
                                                         task_id=self._task_id)
        mock_run.assert_has_calls(
            [mock.call(expected_cmd, capture_output=True, text=True, cwd=None), mocked_index_call])
