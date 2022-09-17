import os
import shutil
import unittest

from google.protobuf.json_format import MessageToDict
import yaml

from common_utils.sandbox import SandboxError
from controller.utils.invoker_call import make_invoker_cmd_call
from controller.utils.invoker_mapping import RequestTypeToInvoker
from id_definition.error_codes import CTLResponseCode, UpdaterErrorCode
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
                os.makedirs(os.path.join(self._sandbox_a_root, user_id, repo_id))

            labels_dict = {'labels': [], 'version': 1, 'ymir_version': '42.0.0'}
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
        for user_id, repo_ids in {'0001': ['000001', '000002'], '0002': ['000001']}.items():
            os.makedirs(os.path.join(self._sandbox_c_root, user_id))

            for repo_id in repo_ids:
                os.makedirs(os.path.join(self._sandbox_c_root, user_id, repo_id))

            labels_dict = {'labels': [], 'version': 1, 'ymir_version': f"0.0.{int(user_id)}"}
            with open(os.path.join(self._sandbox_c_root, user_id, 'labels.yaml'), 'w') as f:
                yaml.safe_dump(labels_dict, f)

    # public: test cases
    def test_all(self) -> None:
        # sandbox a: normal
        response_a = make_invoker_cmd_call(invoker=RequestTypeToInvoker[backend_pb2.SANDBOX_VERSION],
                                           sandbox_root=self._sandbox_a_root,
                                           req_type=backend_pb2.SANDBOX_VERSION)
        print(MessageToDict(response_a))
        self.assertEqual(CTLResponseCode.CTR_OK, response_a.code)
        self.assertEqual('42.0.0', response_a.sandbox_version)

        # sandbox b: no users
        response_b = make_invoker_cmd_call(invoker=RequestTypeToInvoker[backend_pb2.SANDBOX_VERSION],
                                           sandbox_root=self._sandbox_b_root,
                                           req_type=backend_pb2.SANDBOX_VERSION)
        print(MessageToDict(response_b))
        self.assertEqual(CTLResponseCode.CTR_OK, response_b.code)
        self.assertEqual('1.1.0', response_b.sandbox_version)

        # sandbox c: multiple versions
        with self.assertRaises(SandboxError) as e:
            make_invoker_cmd_call(invoker=RequestTypeToInvoker[backend_pb2.SANDBOX_VERSION],
                                  sandbox_root=self._sandbox_c_root,
                                  req_type=backend_pb2.SANDBOX_VERSION)
            self.assertEqual(UpdaterErrorCode.INVALID_USER_SPACE_VERSIONS, e.error_code)
