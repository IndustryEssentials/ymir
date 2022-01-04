import logging
import os
import shutil
import unittest

from google.protobuf.json_format import MessageToDict, ParseDict

import tests.utils as test_utils
from controller import task_monitor
from controller.utils.invoker_call import make_invoker_cmd_call
from controller.utils.invoker_mapping import RequestTypeToInvoker
from proto import backend_pb2

RET_ID = 'commit t000aaaabbbbbbzzzzzzzzzzzzzzz3\nabc'


class TestInvokerTaskInfo(unittest.TestCase):
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
        self._task_id = 't000aaaabbbbbbzzzzzzzzzzzzzzz5'
        self._base_task_id = 't000aaaabbbbbbzzzzzzzzzzzzzzz4'

        self._sandbox_root = test_utils.dir_test_root(self.id().split(".")[-3:])
        self._user_root = os.path.join(self._sandbox_root, self._user_name)
        self._mir_repo_root = os.path.join(self._user_root, self._mir_repo_name)
        self._storage_root = os.path.join(self._sandbox_root, self._storage_name)

    def setUp(self):
        test_utils.check_commands()
        self._prepare_dirs()
        self._prepare_mir_repo()

        # Add a mock task file.
        self._ctr_task_monitor = task_monitor.ControllerTaskMonitor(storage_root=self._storage_root)
        task_info = backend_pb2.TaskMonitorStorageItem()
        self._ctr_task_monitor.save_task(self._task_id, task_info)

        logging.info("preparing done.")

    def tearDown(self):
        if os.path.isdir(self._sandbox_root):
            shutil.rmtree(self._sandbox_root)
        self._ctr_task_monitor.stop_monitor()
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

    def test_invoker_task_info_00(self):
        task_info_req = backend_pb2.ReqGetTaskInfo()
        task_info_req.task_ids.extend([self._task_id])
        response = make_invoker_cmd_call(sandbox_root=self._sandbox_root,
                                         req_type=backend_pb2.TASK_INFO,
                                         invoker=RequestTypeToInvoker[backend_pb2.TASK_INFO],
                                         user_id=self._user_name,
                                         task_id=self._task_id,
                                         repo_id=self._mir_repo_name,
                                         task_info_req=task_info_req)
        print(MessageToDict(response))

        expected_ret = backend_pb2.GeneralResp()
        expected_dict = {'resp_get_task_info': {'task_infos': {self._task_id: {}}}}
        ParseDict(expected_dict, expected_ret)
        self.assertEqual(response, expected_ret)
