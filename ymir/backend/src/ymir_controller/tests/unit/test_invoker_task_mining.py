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
from mir.protos import mir_command_pb2 as mir_cmd_pb
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
        top_k, model_hash, model_stage = 300, 'abc', 'first_stage'
        mine_task_req = backend_pb2.TaskReqMining()
        mine_task_req.top_k = top_k
        in_dataset_ids = [self._guest_id1, self._guest_id2]
        mine_task_req.generate_annotations = False

        req_create_task = backend_pb2.ReqCreateTask()
        req_create_task.task_type = mir_cmd_pb.TaskType.TaskTypeMining
        req_create_task.no_task_monitor = True
        req_create_task.mining.CopyFrom(mine_task_req)
        assets_config = {
            'modelskvlocation': self._storage_root,
            'assetskvlocation': self._storage_root,
            'openpai_host': '',
            'openpai_token': '',
            'openpai_storage': '',
            'openpai_user': '',
            'server_runtime': 'runc',
        }

        working_dir_root = os.path.join(self._sandbox_root, "work_dir",
                                        mir_cmd_pb.TaskType.Name(mir_cmd_pb.TaskType.TaskTypeMining), self._task_id)
        os.makedirs(working_dir_root, exist_ok=True)
        working_dir_0 = os.path.join(working_dir_root, 'sub_task', self._sub_task_id_0)
        os.makedirs(working_dir_0, exist_ok=True)

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
            model_stage=model_stage,
            in_dataset_ids=in_dataset_ids,
            docker_image_config=json.dumps(mining_config),
        )
        print(MessageToDict(response))

        output_config = os.path.join(working_dir_0, 'task_config.yaml')
        with open(output_config, "r") as f:
            config = yaml.safe_load(f)
        mining_config['gpu_id'] = ''
        expected_config = {
            'executor_config': mining_config,
            'task_context': {
                'available_gpu_id': '',
                'server_runtime': 'runc',
            },
        }
        self.assertDictEqual(expected_config, config)

        asset_cache_dir = os.path.join(self._user_root, 'asset_cache')
        mining_cmd = (f"mir mining --root {self._mir_repo_root} "
                      f"--user-label-file {test_utils.user_label_file(self._sandbox_root, self._user_name)} "
                      f"--dst-rev {self._task_id}@{self._task_id} "
                      f"-w {working_dir_0} --model-location {self._storage_root} --media-location {self._storage_root} "
                      f"--model-hash {model_hash}@{model_stage} --src-revs {self._guest_id1};{self._guest_id2} -s host "
                      f"--asset-cache-dir {asset_cache_dir} --task-config-file {output_config} --executor mining_image "
                      f"--executant-name {self._task_id} --topk {top_k}")
        mocked_index_call = test_utils.mocked_index_call(user_id=self._user_name,
                                                         repo_id=self._mir_repo_name,
                                                         task_id=self._task_id)
        mock_run.assert_has_calls(
            [mock.call(mining_cmd.split(' '), capture_output=True, text=True, cwd=None), mocked_index_call])

        expected_ret = backend_pb2.GeneralResp()
        expected_dict = {'message': RET_ID}
        ParseDict(expected_dict, expected_ret)
        self.assertEqual(response, expected_ret)
