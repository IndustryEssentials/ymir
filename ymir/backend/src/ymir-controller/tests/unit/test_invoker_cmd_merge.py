import logging
import os
import shutil
import unittest
from unittest import mock

from google.protobuf.json_format import MessageToDict, ParseDict

import tests.utils as test_utils
from controller.utils.invoker_call import make_invoker_cmd_call
from controller.utils.invoker_mapping import RequestTypeToInvoker
from proto import backend_pb2

RET_ID = 'commit t000aaaabbbbbbzzzzzzzzzzzzzzz3\nabc'


class TestInvokerMerge(unittest.TestCase):
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
        self._dst_dataset_id = 't000aaaabbbbbbzzzzzzzzzzzzzzz4'
        self._guest_id1 = 't000aaaabbbbbbzzzzzzzzzzzzzzz1'
        self._guest_id2 = 't000aaaabbbbbbzzzzzzzzzzzzzzz2'
        self._guest_id3 = 't000aaaabbbbbbzzzzzzzzzzzzzzz3'

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
        response = make_invoker_cmd_call(invoker=RequestTypeToInvoker[backend_pb2.CMD_MERGE],
                                         sandbox_root=self._sandbox_root,
                                         req_type=backend_pb2.CMD_MERGE,
                                         user_id=self._user_name,
                                         repo_id=self._mir_repo_name,
                                         task_id=self._task_id,
                                         his_task_id=self._guest_id1,
                                         dst_dataset_id=self._dst_dataset_id,
                                         in_dataset_ids=[self._guest_id1, self._guest_id2],
                                         ex_dataset_ids=[self._guest_id3],
                                         merge_strategy=backend_pb2.MergeStrategy.Value('HOST'))
        print(MessageToDict(response))

        working_dir = os.path.join(self._sandbox_root, "work_dir", backend_pb2.RequestType.Name(backend_pb2.CMD_MERGE),
                                   self._task_id)
        os.makedirs(working_dir, exist_ok=True)

        expected_cmd = ("mir merge --root {0} --dst-rev {1}@{2} -s host -w {3} "
                        "--src-revs {4}@{4};{5} --ex-src-revs {6}".format(self._mir_repo_root, self._dst_dataset_id,
                                                                          self._task_id, working_dir, self._guest_id1,
                                                                          self._guest_id2, self._guest_id3))
        mock_run.assert_called_once_with(expected_cmd.split(' '), capture_output=True, text=True)

        expected_ret = backend_pb2.GeneralResp()
        expected_dict = {'message': RET_ID}
        ParseDict(expected_dict, expected_ret)
        self.assertEqual(response, expected_ret)
