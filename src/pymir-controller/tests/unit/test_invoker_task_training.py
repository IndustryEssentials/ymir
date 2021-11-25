import json
import logging
import os
import shutil
import unittest
from unittest import mock

import yaml
from google.protobuf.json_format import MessageToDict, ParseDict

import tests.utils as test_utils
from controller.utils import utils, gpu_utils
from controller.utils.invoker_call import make_invoker_cmd_call
from controller.utils.invoker_mapping import RequestTypeToInvoker
from controller.utils.labels import LabelFileHandler
from controller.utils.redis import rds
from proto import backend_pb2

RET_ID = 'commit t000aaaabbbbbbzzzzzzzzzzzzzzz3\nabc'


class TestInvokerTaskTraining(unittest.TestCase):
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
        self._task_id = 't000aaaabbbbbbzzzzzzzzzzzzzzd5'
        self._sub_task_id = utils.sub_task_id(self._task_id, 1)
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
        rds.zrange = mock.Mock(return_value=['0', '2'])
        rds.zadd = mock.Mock()
        rds.zremrangebyscore = mock.Mock()
        gpu_utils.get_gpus_info = mock.Mock(return_value={'0': 0.99, '1': 0.9, '2': 0.89})

        LabelFileHandler.get_main_labels_by_ids = mock.Mock(return_value=["frisbee", "car"])

        training_config = {
            'anchors': '12, 16, 19, 36, 40, 28, 36, 75, 76, 55, 72, 146, 142, 110, 192, 243, 459, 401',
            'batch': 64,
            'gpu_id': '4',
            'image_height': 608,
            'image_width': 608,
            'learning_rate': 0.013,
            'max_batches': 20000,
            'pretrained_model_params': '/fake_model',
            'shm_size': '16G',
            'subdivisions': 32,
            'warmup_iterations': 1000
        }

        training_data_type_1 = backend_pb2.TaskReqTraining.TrainingDatasetType()
        training_data_type_1.dataset_id = self._guest_id1
        training_data_type_1.dataset_type = backend_pb2.TvtType.TvtTypeTraining
        training_data_type_2 = backend_pb2.TaskReqTraining.TrainingDatasetType()
        training_data_type_2.dataset_id = self._guest_id2
        training_data_type_2.dataset_type = backend_pb2.TvtType.TvtTypeValidation

        train_task_req = backend_pb2.TaskReqTraining()
        train_task_req.in_dataset_types.append(training_data_type_1)
        train_task_req.in_dataset_types.append(training_data_type_2)
        train_task_req.in_class_ids[:] = [0, 1]
        train_task_req.training_config = json.dumps(training_config)

        req_create_task = backend_pb2.ReqCreateTask()
        req_create_task.task_type = backend_pb2.TaskTypeTraining
        req_create_task.no_task_monitor = True
        req_create_task.training.CopyFrom(train_task_req)
        training_image = 'test_training_image'
        assets_config = {
            'modelsuploadlocation': self._storage_root,
            'assetskvlocation': self._storage_root,
            'training_image': training_image
        }
        response = make_invoker_cmd_call(invoker=RequestTypeToInvoker[backend_pb2.TASK_CREATE],
                                         sandbox_root=self._sandbox_root,
                                         assets_config=assets_config,
                                         req_type=backend_pb2.TASK_CREATE,
                                         user_id=self._user_name,
                                         repo_id=self._mir_repo_name,
                                         task_id=self._task_id,
                                         req_create_task=req_create_task,
                                         executor_instance=self._task_id,
                                         merge_strategy=backend_pb2.MergeStrategy.Value('HOST'))
        print(MessageToDict(response))

        expected_cmd_merge = ("cd {0} && mir merge --dst-rev {1}@{2} -s host "
                              "--src-revs 'tr:{3}@{3};va:{4}'".format(self._mir_repo_root, self._task_id,
                                                                      self._sub_task_id, self._guest_id1,
                                                                      self._guest_id2))
        working_dir = os.path.join(self._sandbox_root, "work_dir",
                                   backend_pb2.TaskType.Name(backend_pb2.TaskTypeTraining), self._task_id)
        os.makedirs(working_dir, exist_ok=True)

        output_config = os.path.join(working_dir, 'task_config.yaml')
        with open(output_config, "r") as f:
            config = yaml.safe_load(f)

        training_config["class_names"] = ["frisbee", "car"]
        training_config["gpu_id"] = '1'
        self.assertDictEqual(training_config, config)

        training_cmd = ("cd {0} && mir train --dst-rev {1}@{1} --model-location {2} "
                        "--media-location {2} -w {3} --src-revs {1}@{4} --config-file {5} --executor {6} "
                        "--executor-instance {7}".format(
                            self._mir_repo_root, self._task_id, self._storage_root, working_dir, self._sub_task_id,
                            output_config, training_image, self._task_id))
        mock_run.assert_has_calls(calls=[
            mock.call(expected_cmd_merge, capture_output=True, shell=True),
            mock.call(training_cmd, capture_output=True, shell=True),
        ])

        expected_ret = backend_pb2.GeneralResp()
        expected_dict = {'message': RET_ID}
        ParseDict(expected_dict, expected_ret)
        self.assertEqual(response, expected_ret)
