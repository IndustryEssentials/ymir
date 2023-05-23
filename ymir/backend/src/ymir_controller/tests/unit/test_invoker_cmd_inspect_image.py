import os
import shutil
import unittest
from unittest import mock

import tests.utils as test_utils
from controller.config.common_task import IMAGE_CONFIG_SENTINEL
from controller.utils.invoker_call import make_invoker_cmd_call
from controller.utils.invoker_mapping import RequestTypeToInvoker
from id_definition.error_codes import CTLResponseCode
from proto import backend_pb2


class TestInvokerInspectImage(unittest.TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self._user_name = "aaaa"
        self._mir_repo_name = "bbbbbb"
        self._storage_name = "media_storage_root"
        self._task_id = "t000aaaabbbbbbzzzzzzzzzzzzzzz5"

        self._sandbox_root = test_utils.dir_test_root(self.id().split(".")[-3:])
        self._user_root = os.path.join(self._sandbox_root, self._user_name)
        self._mir_repo_root = os.path.join(self._user_root, self._mir_repo_name)
        self._storage_root = os.path.join(self._sandbox_root, self._storage_name)

    def setUp(self):
        test_utils.check_commands()
        self._prepare_dirs()
        # self._prepare_mir_repo()

    def tearDown(self):
        if os.path.isdir(self._sandbox_root):
            shutil.rmtree(self._sandbox_root)

    # custom: env prepare
    def _prepare_dirs(self):
        if os.path.isdir(self._sandbox_root):
            shutil.rmtree(self._sandbox_root)
        os.makedirs(self._sandbox_root)
        os.mkdir(self._user_root)
        os.mkdir(self._mir_repo_root)
        os.mkdir(self._storage_root)

    def _mock_manifest_single_object_type(*args, **kwargs):
        ret = type("", (), {})()
        ret.returncode = CTLResponseCode.CTR_OK
        if "images" in args[0]:
            ret.stdout = "fake_hash"
        else:
            # manifest.yaml & template.yaml
            ret.stdout = f"{IMAGE_CONFIG_SENTINEL}\nobject_type: 2\nis_official: False\nenable_livecode: False"
        return ret

    def _mock_manifest_multi_object_type(*args, **kwargs):
        ret = type("", (), {})()
        ret.returncode = CTLResponseCode.CTR_OK
        if "images" in args[0]:
            ret.stdout = "fake_hash_2"
        else:
            # manifest.yaml & template.yaml
            ret.stdout = f"{IMAGE_CONFIG_SENTINEL}\nobject_type: [2, 4]\nis_official: True"
        return ret

    @mock.patch("subprocess.run", side_effect=_mock_manifest_single_object_type)
    def test_single_object_type_00(self, mock_run):
        response = make_invoker_cmd_call(
            invoker=RequestTypeToInvoker[backend_pb2.CMD_INSPECT_IMAGE],
            sandbox_root=self._sandbox_root,
            req_type=backend_pb2.CMD_INSPECT_IMAGE,
            user_id=self._user_name,
            repo_id=self._mir_repo_name,
            task_id=self._task_id,
            singleton_op="docker_image_name",
        )

        config_paths = [
            '/img-man/manifest.yaml',
            '/img-man/training-template.yaml',
            '/img-man/mining-template.yaml',
            '/img-man/infer-template.yaml',
        ]
        expected_calls_list = [
            mock.call(
                ['docker', 'images', 'docker_image_name', '--format', '{{.ID}}'],
                capture_output=True,
                text=True,
                cwd=None,
            ),
        ]
        expected_calls_list.extend([mock.call(
            ['docker', 'run', '--rm', 'docker_image_name', 'sh', '-c',
             f"echo {IMAGE_CONFIG_SENTINEL} && cat {p}"],
            capture_output=True,
            text=True,
            cwd=None,
        ) for p in config_paths])
        self.assertEqual(expected_calls_list, mock_run.call_args_list)
        self.assertEqual(CTLResponseCode.CTR_OK, response.code)
        self.assertEqual("fake_hash", response.hash_id)
        self.assertEqual({2}, set(response.docker_image_config.keys()))
        self.assertEqual({1, 2, 9}, set(response.docker_image_config[2].config.keys()))
        self.assertFalse(response.docker_image_enable_livecode)
        self.assertFalse(response.docker_image_is_official)

    @mock.patch("subprocess.run", side_effect=_mock_manifest_multi_object_type)
    def test_multi_object_type_00(self, mock_run):
        response = make_invoker_cmd_call(
            invoker=RequestTypeToInvoker[backend_pb2.CMD_INSPECT_IMAGE],
            sandbox_root=self._sandbox_root,
            req_type=backend_pb2.CMD_INSPECT_IMAGE,
            user_id=self._user_name,
            repo_id=self._mir_repo_name,
            task_id=self._task_id,
            singleton_op="docker_image_name",
        )

        config_dirs = ['/img-man/det', '/img-man/instance-seg']
        config_names = ['training-template.yaml', 'mining-template.yaml', 'infer-template.yaml']
        config_paths = ['/img-man/manifest.yaml']
        config_paths.extend([f"{d}/{n}" for d in config_dirs for n in config_names])
        expected_calls_list = [
            mock.call(
                ['docker', 'images', 'docker_image_name', '--format', '{{.ID}}'],
                capture_output=True,
                text=True,
                cwd=None,
            ),
        ]
        expected_calls_list.extend([
            mock.call(
                ['docker', 'run', '--rm', 'docker_image_name', 'sh', '-c',
                 f"echo {IMAGE_CONFIG_SENTINEL} && cat {p}"],
                capture_output=True,
                text=True,
                cwd=None,
            ) for p in config_paths
        ])
        self.assertEqual(expected_calls_list, mock_run.call_args_list)
        self.assertEqual(CTLResponseCode.CTR_OK, response.code)
        self.assertEqual("fake_hash_2", response.hash_id)
        self.assertEqual({2, 4}, set(response.docker_image_config.keys()))
        self.assertEqual({1, 2, 9}, set(response.docker_image_config[2].config.keys()))
        self.assertFalse(response.docker_image_enable_livecode)
        self.assertTrue(response.docker_image_is_official)
