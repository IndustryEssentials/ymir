import os
import shutil
import subprocess
import unittest

from google.protobuf.json_format import MessageToDict
import yaml

from controller.utils.invoker_call import make_invoker_cmd_call
from controller.utils.invoker_mapping import RequestTypeToInvoker
from id_definition.error_codes import CTLResponseCode
from proto import backend_pb2

from tests import utils as test_utils


class TestCmdSandboxVersion(unittest.TestCase):
    # life cycle
    def __init__(self, methodName: str) -> None:
        super().__init__(methodName=methodName)
        self._test_root = test_utils.dir_test_root(self.id().split(".")[-3:])
        self._sandbox_a_root = os.path.join(self._test_root, 'sandbox_a')
        self._sandbox_b_root = os.path.join(self._test_root, 'sandbox_b')
        self._sandbox_c_root = os.path.join(self._test_root, 'sandbox_c')

    def setUp(self) -> None:
        self._prepare_test_root()
        self._prepare_sandbox_a()
        self._prepare_sandbox_b()
        self._prepare_sandbox_c()
        return super().setUp()

    def tearDown(self) -> None:
        self._deprepare_test_root()
        return super().tearDown()

    # protected: prepare and de-prepare
    def _prepare_test_root(self) -> None:
        if os.path.isdir(self._test_root):
            shutil.rmtree(self._test_root)
        os.makedirs(self._test_root, exist_ok=True)

    def _deprepare_test_root(self) -> None:
        if os.path.isdir(self._test_root):
            shutil.rmtree(self._test_root)

    def _prepare_sandbox_a(self) -> None:
        """
        sandbox a: sandbox with two users
        """
        os.makedirs(self._sandbox_a_root)

        for user_id, repo_ids in {'0001': ['000001', '000002'], '0002': ['000001']}.items():
            os.makedirs(os.path.join(self._sandbox_a_root, user_id))

            for repo_id in repo_ids:
                self._prepare_repo(os.path.join(self._sandbox_a_root, user_id, repo_id))

            labels_dict = {'labels': [], 'version': 1, 'ymir_version': '2.0.0'}
            with open(os.path.join(self._sandbox_a_root, user_id, 'labels.yaml'), 'w') as f:
                yaml.safe_dump(labels_dict, f)

    def _prepare_sandbox_b(self) -> None:
        """
        sandbox b: an empty sandbox
        """
        os.makedirs(self._sandbox_b_root)

    def _prepare_sandbox_c(self) -> None:
        """
        sandbox c: sandbox with multiple user space versions
        """
        vers = {'0001': '1.1.0', '0002': '2.0.0'}
        for user_id, repo_ids in {'0001': ['000001', '000002'], '0002': ['000001']}.items():
            os.makedirs(os.path.join(self._sandbox_c_root, user_id))

            for repo_id in repo_ids:
                self._prepare_repo(os.path.join(self._sandbox_c_root, user_id, repo_id))

            labels_dict = {'labels': [], 'version': 1, 'ymir_version': vers[user_id]}
            with open(os.path.join(self._sandbox_c_root, user_id, 'labels.yaml'), 'w') as f:
                yaml.safe_dump(labels_dict, f)

    @classmethod
    def _prepare_repo(cls, mir_root: str) -> None:
        os.makedirs(mir_root, exist_ok=True)
        subprocess.run(['git', 'config', '--global', 'init.defaultBranch', 'master'], cwd=mir_root)
        subprocess.run(['git', 'init'], cwd=mir_root)

    # public: test cases
    def test_all(self) -> None:
        # sandbox a: normal
        response_a = make_invoker_cmd_call(invoker=RequestTypeToInvoker[backend_pb2.CMD_VERSIONS_GET],
                                           sandbox_root=self._sandbox_a_root,
                                           req_type=backend_pb2.CMD_VERSIONS_GET)
        print(MessageToDict(response_a))
        self.assertEqual(CTLResponseCode.CTR_OK, response_a.code)
        self.assertEqual(['2.0.0'], response_a.sandbox_versions)

        # sandbox b: no users
        response_b = make_invoker_cmd_call(invoker=RequestTypeToInvoker[backend_pb2.CMD_VERSIONS_GET],
                                           sandbox_root=self._sandbox_b_root,
                                           req_type=backend_pb2.CMD_VERSIONS_GET)
        self.assertEqual([], response_b.sandbox_versions)

        # sandbox c: multiple versions
        response_c = make_invoker_cmd_call(invoker=RequestTypeToInvoker[backend_pb2.CMD_VERSIONS_GET],
                                           sandbox_root=self._sandbox_c_root,
                                           req_type=backend_pb2.CMD_VERSIONS_GET)
        self.assertEqual({'1.1.0', '2.0.0'}, set(response_c.sandbox_versions))
