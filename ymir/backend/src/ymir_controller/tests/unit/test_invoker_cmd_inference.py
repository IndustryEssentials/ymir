import json
import logging
import os
import shutil
import unittest
from unittest import mock

import tests.utils as test_utils
from controller.invoker.invoker_cmd_inference import InferenceCMDInvoker
from controller.utils.invoker_call import make_invoker_cmd_call
from controller.utils.invoker_mapping import RequestTypeToInvoker
from proto import backend_pb2


class TestInvokerCMDInference(unittest.TestCase):
    def __init__(self, methodName: str) -> None:
        super().__init__(methodName=methodName)
        self._user_name = "user"
        self._mir_repo_name = "repoid"
        self._storage_name = "media_storage_root"
        self._tensorboard_root_name = "tensorboard_root"
        self._task_id = "t000aaaabbbbbbzzzzzzzzzzzzzzd5"

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
        ret = type("", (), {})()
        ret.returncode = 0
        ret.stdout = "mock sub run return"
        return ret

    @mock.patch("subprocess.run", side_effect=_mock_run_func)
    def test_invoker_00(self, mock_run):
        training_config = {
            "anchors": "12, 16, 19, 36, 40, 28, 36, 75, 76, 55",
            "batch": 64,
            "image_height": 608,
            "image_width": 608,
            "learning_rate": 0.013,
            "max_batches": 20000,
            "pretrained_model_params": "/fake_model",
            "shm_size": "16G",
            "subdivisions": 32,
            "warmup_iterations": 1000,
        }
        inference_image = "test_infer_image"
        model_hash = "model_hash_id"
        assets_config = {
            "modelskvlocation": self._storage_root,
        }

        mock_json = {
            "detection": {
                "pic_hash": {
                    "annotations": [{
                        "box": {
                            "x": 300,
                            "y": 35,
                            "w": 81,
                            "h": 88
                        },
                        "class_name": "no_helmet_head",
                        "score": 0.991247296333313,
                        "class_id": 3,
                    }],
                }
            }
        }

        with mock.patch.object(InferenceCMDInvoker, "get_inference_result", return_value=mock_json):
            make_invoker_cmd_call(
                invoker=RequestTypeToInvoker[backend_pb2.CMD_INFERENCE],
                sandbox_root=self._sandbox_root,
                assets_config=assets_config,
                req_type=backend_pb2.CMD_INFERENCE,
                user_id=self._user_name,
                repo_id=self._mir_repo_name,
                task_id=self._task_id,
                singleton_op=inference_image,
                docker_image_config=json.dumps(training_config),
                model_hash=model_hash,
            )

        working_dir = os.path.join(self._sandbox_root, "work_dir",
                                   backend_pb2.RequestType.Name(backend_pb2.CMD_INFERENCE), self._task_id)
        os.makedirs(working_dir, exist_ok=True)
        config_file = os.path.join(working_dir, "inference_config.yaml")

        index_file = os.path.join(working_dir, "inference_pic_index.txt")

        cmd = (f"mir infer --root {self._mir_repo_root} -w {working_dir} --model-location {self._storage_root} "
               f"--index-file {index_file} --model-hash {model_hash} "
               f"--task-config-file {config_file} --executor {inference_image}")

        mock_run.assert_has_calls(calls=[
            mock.call(cmd.split(' '), capture_output=True, text=True),
        ])
