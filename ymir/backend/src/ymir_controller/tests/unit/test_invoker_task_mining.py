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
        self._sub_task_id_0 = utils.sub_task_id(self._task_id, 0)
        self._sub_task_id_1 = utils.sub_task_id(self._task_id, 1)
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
            'class_names': [],
            'model_name': 'yolo',
            'model_type': 'detection',
            'strategy': 'aldd_yolo',
            'image_height': 608,
            'image_width': 608,
            'batch_size': 16,
            'gpu_count': 0
        }
        top_k, model_hash = 300, 'abc'
        mine_task_req = backend_pb2.TaskReqMining()
        mine_task_req.top_k = top_k
        mine_task_req.in_dataset_ids[:] = [self._guest_id1, self._guest_id2]
        mine_task_req.ex_dataset_ids[:] = [self._guest_id3]
        mine_task_req.generate_annotations = False

        req_create_task = backend_pb2.ReqCreateTask()
        req_create_task.task_type = backend_pb2.TaskTypeMining
        req_create_task.no_task_monitor = True
        req_create_task.mining.CopyFrom(mine_task_req)
        assets_config = {
            'modelskvlocation': self._storage_root,
            'assetskvlocation': self._storage_root,
        }

        working_dir_root = os.path.join(self._sandbox_root, "work_dir",
                                        backend_pb2.TaskType.Name(backend_pb2.TaskTypeMining), self._task_id)
        os.makedirs(working_dir_root, exist_ok=True)
        working_dir_0 = os.path.join(working_dir_root, 'sub_task', self._sub_task_id_0)
        os.makedirs(working_dir_0, exist_ok=True)
        working_dir_1 = os.path.join(working_dir_root, 'sub_task', self._sub_task_id_1)
        os.makedirs(working_dir_1, exist_ok=True)

        expected_cmd_merge = ("mir merge --root {0} --dst-rev {1}@{2} -s host -w {3} "
                              "--src-revs {4}@{4};{5} --ex-src-revs {6}".format(self._mir_repo_root, self._task_id,
                                                                                self._sub_task_id_1, working_dir_1,
                                                                                self._guest_id1, self._guest_id2,
                                                                                self._guest_id3))

        response = make_invoker_cmd_call(
            invoker=RequestTypeToInvoker[backend_pb2.TASK_CREATE],
            sandbox_root=self._sandbox_root,
            assets_config=assets_config,
            req_type=backend_pb2.TASK_CREATE,
            user_id=self._user_name,
            repo_id=self._mir_repo_name,
            task_id=self._task_id,
            req_create_task=req_create_task,
            merge_strategy=backend_pb2.MergeStrategy.Value('HOST'),
            singleton_op='mining_image',
            model_hash=model_hash,
            docker_image_config=json.dumps(mining_config),
        )
        print(MessageToDict(response))

        output_config = os.path.join(working_dir_0, 'task_config.yaml')
        with open(output_config, "r") as f:
            config = yaml.safe_load(f)
        mining_config['gpu_id'] = ''
        expected_config = {'executor_config': mining_config, 'task_context': {'available_gpu_id': ''}}
        self.assertDictEqual(expected_config, config)

        asset_cache_dir = os.path.join(self._user_root, 'mining_assset_cache')
        mining_cmd = ("mir mining --root {0} --dst-rev {1}@{1} -w {2} --model-location {3} --media-location {3} "
                      "--model-hash {5} --src-revs {1}@{6} --asset-cache-dir {9} --task-config-file {7} --executor {8} "
                      "--executant-name {10} --topk {4}".format(self._mir_repo_root, self._task_id, working_dir_0,
                                                                self._storage_root, top_k, model_hash,
                                                                self._sub_task_id_1, output_config, 'mining_image',
                                                                asset_cache_dir, self._task_id))
        mock_run.assert_has_calls(calls=[
            mock.call(expected_cmd_merge.split(' '), capture_output=True, text=True),
            mock.call(mining_cmd.split(' '), capture_output=True, text=True),
        ])

        expected_ret = backend_pb2.GeneralResp()
        expected_dict = {'message': RET_ID}
        ParseDict(expected_dict, expected_ret)
        self.assertEqual(response, expected_ret)
