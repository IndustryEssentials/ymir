import logging
import os
import shutil
import unittest
from unittest import mock

from google.protobuf.json_format import MessageToDict, ParseDict

import tests.utils as test_utils
from controller.utils.invoker_call import make_invoker_cmd_call
from controller.utils.invoker_mapping import RequestTypeToInvoker
from controller.utils.labels import LabelFileHandler
from proto import backend_pb2

RET_ID = 'commit t000aaaabbbbbbzzzzzzzzzzzzzzz3\nabc'


class TestInvokerFilterBranch(unittest.TestCase):
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
        self.in_dataset_ids = ['t000aaaabbbbbbzzzzzzzzzzzzzzz4']

        self._sandbox_root = test_utils.dir_test_root(self.id().split(".")[-3:])
        self._user_root = os.path.join(self._sandbox_root, self._user_name)
        self._mir_repo_root = os.path.join(self._user_root, self._mir_repo_name)
        self._storage_root = os.path.join(self._sandbox_root, self._storage_name)

    def setUp(self):
        test_utils.check_commands()
        self._prepare_dirs()
        self._prepare_mir_repo()
        logging.info("preparing done.")

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
        LabelFileHandler.get_main_labels_by_ids = mock.Mock(return_value=["car", "person"])
        LabelFileHandler.get_main_labels_by_ids = mock.Mock(return_value=["car", "person"])
        in_class_ids = [1, 2]
        ex_class_ids = [3]
        response = make_invoker_cmd_call(invoker=RequestTypeToInvoker[backend_pb2.CMD_FILTER],
                                         sandbox_root=self._sandbox_root,
                                         req_type=backend_pb2.CMD_FILTER,
                                         user_id=self._user_name,
                                         repo_id=self._mir_repo_name,
                                         task_id=self._task_id,
                                         his_task_id=self.in_dataset_ids[0],
                                         dst_task_id=self._task_id,
                                         in_dataset_ids=self.in_dataset_ids,
                                         in_class_ids=in_class_ids,
                                         ex_class_ids=ex_class_ids)
        print(MessageToDict(response))

        expected_cmd = "cd {0} && mir filter --dst-rev {1}@{1} --src-revs {2}@{2} -p '{3}' -P '{4}'".format(
            self._mir_repo_root, self._task_id, self.in_dataset_ids[0], 'car;person', 'car;person')
        mock_run.assert_called_once_with(expected_cmd, capture_output=True, shell=True)

        expected_ret = backend_pb2.GeneralResp()
        expected_dict = {'message': RET_ID}
        ParseDict(expected_dict, expected_ret)
        self.assertEqual(response, expected_ret)
