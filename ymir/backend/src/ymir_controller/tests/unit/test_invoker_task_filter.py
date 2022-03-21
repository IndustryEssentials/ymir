import logging
import os
import shutil
import unittest
from unittest import mock

from google.protobuf.json_format import MessageToDict, ParseDict


from common_utils import labels
from controller.utils import utils
from controller.utils.invoker_call import make_invoker_cmd_call
from controller.utils.invoker_mapping import RequestTypeToInvoker
from proto import backend_pb2
import tests.utils as test_utils

RET_ID = 'commit t000aaaabbbbbbzzzzzzzzzzzzzzz3\nabc'


class TestInvokerTaskFilter(unittest.TestCase):
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
        self._task_id = 't000aaaabbbbbbzzzzzzzzzzzzzza5'
        self._sub_task_id_0 = utils.sub_task_id(self._task_id, 0)
        self._sub_task_id_1 = utils.sub_task_id(self._task_id, 1)
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
        labels.UserLabels.get_main_names = mock.Mock(return_value=["frisbee", "car"])
        filter_request = backend_pb2.TaskReqFilter()
        filter_request.in_dataset_ids[:] = [self._guest_id1, self._guest_id2]
        filter_request.in_class_ids[:] = [0, 1]
        filter_request.ex_class_ids[:] = [2]
        req_create_task = backend_pb2.ReqCreateTask()
        req_create_task.task_type = backend_pb2.TaskTypeFilter
        req_create_task.no_task_monitor = True
        req_create_task.filter.CopyFrom(filter_request)

        working_dir_root = os.path.join(self._sandbox_root, "work_dir",
                                        backend_pb2.TaskType.Name(backend_pb2.TaskTypeFilter), self._task_id)
        os.makedirs(working_dir_root, exist_ok=True)
        working_dir_0 = os.path.join(working_dir_root, 'sub_task', self._sub_task_id_0)
        os.makedirs(working_dir_0, exist_ok=True)
        working_dir_1 = os.path.join(working_dir_root, 'sub_task', self._sub_task_id_1)
        os.makedirs(working_dir_1, exist_ok=True)

        response = make_invoker_cmd_call(invoker=RequestTypeToInvoker[backend_pb2.TASK_CREATE],
                                         sandbox_root=self._sandbox_root,
                                         req_type=backend_pb2.TASK_CREATE,
                                         user_id=self._user_name,
                                         repo_id=self._mir_repo_name,
                                         task_id=self._task_id,
                                         req_create_task=req_create_task,
                                         merge_strategy=backend_pb2.MergeStrategy.Value('HOST'),
                                         work_dir=working_dir_root)
        print(MessageToDict(response))

        expected_cmd_merge = ("mir merge --root {0} --dst-rev {1}@{2} -s host -w {3} "
                              "--src-revs {4}@{4};{5}".format(self._mir_repo_root, self._task_id, self._sub_task_id_1,
                                                              working_dir_1, self._guest_id1, self._guest_id2))
        expected_cmd_filter = ("mir filter --root {0} --dst-rev {1}@{1} --src-revs {1}@{2} -w {3} "
                               "-p {4} -P {5}".format(self._mir_repo_root, self._task_id, self._sub_task_id_1,
                                                      working_dir_0, 'frisbee;car', 'frisbee;car'))
        mock_run.assert_has_calls(calls=[
            mock.call(expected_cmd_merge.split(' '), capture_output=True, text=True),
            mock.call(expected_cmd_filter.split(' '), capture_output=True, text=True),
        ])

        expected_ret = backend_pb2.GeneralResp()
        expected_dict = {'message': RET_ID}
        ParseDict(expected_dict, expected_ret)
        self.assertEqual(response, expected_ret)
