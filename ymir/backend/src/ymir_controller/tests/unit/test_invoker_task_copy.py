import logging
import os
import shutil
import unittest
from unittest import mock

from google.protobuf.json_format import ParseDict

import tests.utils as test_utils
from controller.utils import utils
from controller.utils.invoker_call import make_invoker_cmd_call
from controller.utils.invoker_mapping import RequestTypeToInvoker
from proto import backend_pb2

RET_ID = 'commit t000aaaabbbbbbzzzzzzzzzzzzzzz3\nabc'


class TestInvokerTaskCopy(unittest.TestCase):
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
        self._task_id = 't000aaaabbbbbbzzzzzzzzzzzzzzb5'
        self._sub_task_id = utils.sub_task_id(self._task_id, 1)
        self._base_task_id = 't000aaaabbbbbbzzzzzzzzzzzzzzz4'
        self._guest_id1 = 't000aaaabbbbbbzzzzzzzzzzzzzzz1'
        self._guest_id2 = 't000aaaabbbbbbzzzzzzzzzzzzzzz2'

        self._sandbox_root = test_utils.dir_test_root(self.id().split(".")[-3:])
        self._user_root = os.path.join(self._sandbox_root, self._user_name)
        self._mir_repo_root = os.path.join(self._user_root, self._mir_repo_name)
        self._storage_root = os.path.join(self._sandbox_root, self._storage_name)

    def setUp(self):
        test_utils.check_commands()
        self._prepare_dirs()
        self._prepare_mir_repo()
        self._prepare_assets()

        logging.info("preparing done.")

    def _prepare_assets(self):
        image_names = ["1.jpg", "2.jpg"]
        for image_name in image_names:
            with open(os.path.join(self._storage_root, image_name), 'w') as f:
                f.write("1")

    def tearDown(self):
        if os.path.isdir(self._sandbox_root):
            shutil.rmtree(self._sandbox_root)
        pass

    # custom: env prepare
    def _prepare_dirs(self):
        if os.path.isdir(self._sandbox_root):
            logging.info("sandbox root exists, remove it first")
            shutil.rmtree(self._sandbox_root)
        os.makedirs(self._sandbox_root)
        os.mkdir(self._user_root)
        os.mkdir(self._mir_repo_root)
        os.mkdir(self._storage_root)

    def _prepare_mir_repo(self):
        # init repo
        test_utils.mir_repo_init(self._mir_repo_root)
        # prepare branch a

    def _mock_run_func(*args, **kwargs):
        ret = type('', (), {})()
        ret.returncode = 0
        ret.stdout = RET_ID
        return ret

    @mock.patch("subprocess.run", side_effect=_mock_run_func)
    def test_invoker_00(self, mock_run):
        copy_request = backend_pb2.TaskReqCopyData()
        copy_request.src_user_id = "usre"
        copy_request.src_repo_id = "repodi"
        copy_request.src_dataset_id = "t000aaaabbbbbbzzzzzzzzzzzzzzb6"
        mir_src_root = os.path.join(self._sandbox_root, copy_request.src_user_id, copy_request.src_repo_id)
        os.makedirs(mir_src_root)
        working_dir = os.path.join(self._sandbox_root, "work_dir",
                                   backend_pb2.TaskType.Name(backend_pb2.TaskTypeCopyData), self._task_id, 'sub_task',
                                   self._task_id)

        req_create_task = backend_pb2.ReqCreateTask()
        req_create_task.task_type = backend_pb2.TaskTypeCopyData
        req_create_task.no_task_monitor = True
        req_create_task.copy.CopyFrom(copy_request)
        response = make_invoker_cmd_call(invoker=RequestTypeToInvoker[backend_pb2.TASK_CREATE],
                                         sandbox_root=self._sandbox_root,
                                         req_type=backend_pb2.TASK_CREATE,
                                         user_id=self._user_name,
                                         repo_id=self._mir_repo_name,
                                         task_id=self._task_id,
                                         req_create_task=req_create_task)

        expected_cmd_copy = ("mir copy --root {0} --src-root {1} --dst-rev {2}@{2} --src-revs {3}@{3} -w {4}".format(
            self._mir_repo_root, mir_src_root, self._task_id, copy_request.src_dataset_id, working_dir))
        mock_run.assert_has_calls(calls=[
            mock.call(expected_cmd_copy.split(' '), capture_output=True, text=True),
        ])

        expected_ret = backend_pb2.GeneralResp()
        expected_dict = {'message': RET_ID}
        ParseDict(expected_dict, expected_ret)
        self.assertEqual(response, expected_ret)
