import json
import logging
import os
import shutil
import unittest
from unittest import mock

import yaml
from google.protobuf.json_format import MessageToDict, ParseDict

import tests.utils as test_utils
from controller.utils import utils
from controller.utils.invoker_call import make_invoker_cmd_call
from controller.utils.invoker_mapping import RequestTypeToInvoker
from proto import backend_pb2

RET_ID = 'commit t000aaaabbbbbbzzzzzzzzzzzzzzz3\nabc'


class TestInvokerTaskMining(unittest.TestCase):
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
        self._task_id = 't000aaaabbbbbbzzzzzzzzzzzzzzc5'
        self._sub_task_id = utils.sub_task_id(self._task_id, 1)
        self._base_task_id = 't000aaaabbbbbbzzzzzzzzzzzzzzz4'
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
        mining_config = {
            'data_workers': 28,
            'model_name': 'yolo',
            'model_type': 'detection',
            'strategy': 'aldd_yolo',
            'image_height': 608,
            'image_width': 608,
            'batch_size': 16
        }
        top_k, model_hash = 300, 'abc'
        mine_task_req = backend_pb2.TaskReqMining()
        mine_task_req.top_k = top_k
        mine_task_req.model_hash = model_hash
        mine_task_req.in_dataset_ids[:] = [self._guest_id1, self._guest_id2]
        mine_task_req.ex_dataset_ids[:] = [self._guest_id3]
        mine_task_req.mining_config = json.dumps(mining_config)

        req_create_task = backend_pb2.ReqCreateTask()
        req_create_task.task_type = backend_pb2.TaskTypeMining
        req_create_task.no_task_monitor = True
        req_create_task.mining.CopyFrom(mine_task_req)
        assets_config = {
            'modelskvlocation': self._storage_root,
            'assetskvlocation': self._storage_root,
            'mining_image': 'mining_image'
        }
        response = make_invoker_cmd_call(invoker=RequestTypeToInvoker[backend_pb2.TASK_CREATE],
                                         sandbox_root=self._sandbox_root,
                                         assets_config=assets_config,
                                         req_type=backend_pb2.TASK_CREATE,
                                         user_id=self._user_name,
                                         repo_id=self._mir_repo_name,
                                         task_id=self._task_id,
                                         req_create_task=req_create_task)
        print(MessageToDict(response))

        expected_cmd_merge = ("cd {0} && mir merge --dst-rev {1}@{2} -s stop "
                              "--src-revs '{3}@{3};{4}' --ex-src-revs '{5}'".format(self._mir_repo_root, self._task_id,
                                                                                    self._sub_task_id, self._guest_id1,
                                                                                    self._guest_id2, self._guest_id3))
        working_dir = os.path.join(self._sandbox_root, "work_dir", backend_pb2.TaskType.Name(backend_pb2.TaskTypeMining),
                                   self._task_id)
        os.makedirs(working_dir, exist_ok=True)

        output_config = os.path.join(working_dir, 'task_config.yaml')
        with open(output_config, "r") as f:
            config = yaml.safe_load(f)
        self.assertDictEqual(mining_config, config)

        asset_cache_dir = os.path.join(self._user_root, 'mining_assset_cache')
        mining_cmd = (
            "cd {0} && mir mining --dst-rev {1}@{1} -w {2} --model-location {3} --media-location {3} "
            "--topk {4} --model-hash {5} --src-revs {1}@{6} --cache {9} --config-file {7} --executor {8}".format(
                self._mir_repo_root, self._task_id, working_dir, self._storage_root, top_k, model_hash,
                self._sub_task_id, output_config, assets_config['mining_image'], asset_cache_dir))
        mock_run.assert_has_calls(calls=[
            mock.call(expected_cmd_merge, capture_output=True, shell=True),
            mock.call(mining_cmd, capture_output=True, shell=True),
        ])

        expected_ret = backend_pb2.GeneralResp()
        expected_dict = {'message': RET_ID}
        ParseDict(expected_dict, expected_ret)
        self.assertEqual(response, expected_ret)
